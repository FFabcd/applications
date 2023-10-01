import os
from typing import Dict, Union, Optional
from typing import List
from LangChainCFG import LangChainCFG
from accelerate import load_checkpoint_and_dispatch
from langchain.llms.base import LLM
from langchain.llms.utils import enforce_stop_tokens
from transformers import AutoModel, AutoTokenizer
"""
LLM �Ǵ�������ģ�ͣ�Large Language Models������д��
���� LangChain �ĺ��������
LangChain ƽ̨�ṩ������� LLM �ṩ��
���� OpenAI��Cohere �� Hugging Face�������ı�׼�ӿڡ�
LLM ���ڸ���������ʾ�����ı������������Է��롢�ı���ȫ��������ȶ�������
��������Ȼ���Դ����ǿ�󹤾ߣ���ͨ�� LangChain ƽ̨���ʡ�
"""
class ChatGLMService(LLM):
    max_token: int = 10000  #��������
    temperature: float = 0.1 # �ɱ��
    top_p = 0.9 # ���ɱ��
    history = []  # ��ʷ
    tokenizer: object = None
    model: object = None

    def __init__(self):
        super().__init__()
    @property
    def _llm_type(self) -> str:
        return "ChatGLM"

    def _call(self,
              prompt: str,
              stop: Optional[List[str]] = None) -> str:
        response, _ = self.model.chat(
            self.tokenizer,
            prompt,
            history=self.history,
            max_length=self.max_token,
            temperature=self.temperature,
        )
        if stop is not None:
            response = enforce_stop_tokens(response, stop)
        self.history = self.history + [[None, response]]
        return response

    def load_model(self,
                   model_name_or_path: str = "THUDM/chatglm-6b"):
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name_or_path,
            trust_remote_code=True
        )
        self.model = AutoModel.from_pretrained(model_name_or_path, trust_remote_code=True).half().cuda()
        self.model = self.model.eval()

    def auto_configure_device_map(self, num_gpus: int) -> Dict[str, int]:
        # transformer.word_embeddings ռ��1��
        # transformer.final_layernorm �� lm_head ռ��1��
        # transformer.layers ռ�� 28 ��
        # �ܹ�30����䵽num_gpus�ſ���
        num_trans_layers = 28
        per_gpu_layers = 30 / num_gpus

        # bugfix: ��linux�е���torch.embedding�����weight,input����ͬһdevice��,����RuntimeError
        # windows�� model.device �ᱻ���ó� transformer.word_embeddings.device
        # linux�� model.device �ᱻ���ó� lm_head.device
        # �ڵ���chat����stream_chatʱ,input_ids�ᱻ�ŵ�model.device��
        # ���transformer.word_embeddings.device��model.device��ͬ,��ᵼ��RuntimeError
        # ������ｫtransformer.word_embeddings,transformer.final_layernorm,lm_head���ŵ���һ�ſ���
        device_map = {'transformer.word_embeddings': 0,
                      'transformer.final_layernorm': 0, 'lm_head': 0}

        used = 2
        gpu_target = 0
        for i in range(num_trans_layers):
            if used >= per_gpu_layers:
                gpu_target += 1
                used = 0
            assert gpu_target < num_gpus
            device_map[f'transformer.layers.{i}'] = gpu_target
            used += 1

        return device_map

    def load_model_on_gpus(self, model_name_or_path: Union[str, os.PathLike], num_gpus: int = 2,
                           multi_gpu_model_cache_dir: Union[str, os.PathLike] = "./temp_model_dir",
                           ):
        # https://github.com/THUDM/ChatGLM-6B/issues/200
        self.model = AutoModel.from_pretrained(model_name_or_path, trust_remote_code=True, )
        self.model = self.model.eval()

        device_map = self.auto_configure_device_map(num_gpus)
        try:
            self.model = load_checkpoint_and_dispatch(
                self.model, model_name_or_path, device_map=device_map, offload_folder="offload",
                offload_state_dict=True).half()
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name_or_path,
                trust_remote_code=True
            )
        except ValueError:
            # index.json not found
            print(f"index.json not found, auto fixing and saving model to {multi_gpu_model_cache_dir} ...")

            assert multi_gpu_model_cache_dir is not None, "using auto fix, cache_dir must not be None"
            self.model.save_pretrained(multi_gpu_model_cache_dir, max_shard_size='2GB')
            self.model = load_checkpoint_and_dispatch(
                self.model, multi_gpu_model_cache_dir, device_map=device_map,
                offload_folder="offload", offload_state_dict=True).half()
            self.tokenizer = AutoTokenizer.from_pretrained(
                multi_gpu_model_cache_dir,
                trust_remote_code=True
            )
            print(f"loading model successfully, you should use checkpoint_path={multi_gpu_model_cache_dir} next time")