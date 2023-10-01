import os
from typing import Dict, Union, Optional
from typing import List
from LangChainCFG import LangChainCFG
from accelerate import load_checkpoint_and_dispatch
from langchain.llms.base import LLM
from langchain.llms.utils import enforce_stop_tokens
from transformers import AutoModel, AutoTokenizer
"""
LLM &#65533;1&#65533;7&#65533;0&#65533;6&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;0&#65533;0&#65533;1&#65533;7&#65533;0&#65533;5&#65533;1&#65533;7Large Language Models&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;&#1348;1&#65533;7&#65533;1&#65533;7
&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7 LangChain &#65533;1&#65533;7&#65533;0&#65533;2&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7
LangChain &#65533;0&#65533;9&#65533;0&#65533;6&#65533;1&#65533;7&#65533;5&#65533;9&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7 LLM &#65533;1&#65533;7&#65533;5&#65533;9&#65533;1&#65533;7&#65533;1&#65533;7
&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7 OpenAI&#65533;1&#65533;7&#65533;1&#65533;7Cohere &#65533;1&#65533;7&#65533;1&#65533;7 Hugging Face&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;0&#65533;3&#65533;1&#65533;7&#65533;0&#65533;6&#65533;1&#65533;7&#65533;0&#65533;3&#65533;1&#65533;1&#65533;1&#65533;7
LLM &#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;4&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;0&#65533;5&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;0&#65533;3&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;0&#65533;9&#65533;1&#65533;7&#65533;1&#65533;7&#65533;0&#65533;5&#65533;1&#65533;7&#65533;0&#65533;3&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;0&#65533;0&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;0&#65533;1&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7
&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;0&#65533;6&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;0&#65533;6&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;0&#65533;6&#65533;1&#65533;7&#65533;9&#65533;4&#65533;1&#65533;3&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;0&#65533;0&#65533;1&#65533;7&#65533;1&#65533;7 LangChain &#65533;0&#65533;9&#65533;0&#65533;6&#65533;1&#65533;7&#65533;1&#65533;7&#65533;1&#65533;7&#65533;0&#65533;6&#65533;1&#65533;7
"""
class ChatGLMService(LLM):
    max_token: int = 10000  #&#65533;&#65533;&#65533;&#65533;&#65533;&#65533;&#65533;&#65533;
    temperature: float = 0.1 # &#65533;&#625;&#65533;&#65533;
    top_p = 0.9 # &#65533;&#65533;&#65533;&#625;&#65533;&#65533;
    history = []  # &#65533;&#65533;&#695;
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
        # transformer.word_embeddings 占用1层
        # transformer.final_layernorm 和 lm_head 占用1层
        # transformer.layers 占用 28 层
        # 总共30层分配到num_gpus张卡上
        num_trans_layers = 28
        per_gpu_layers = 30 / num_gpus

        # bugfix: 在linux中调用torch.embedding传入的weight,input不在同一device上,导致RuntimeError
        # windows下 model.device 会被设置成 transformer.word_embeddings.device
        # linux下 model.device 会被设置成 lm_head.device
        # 在调用chat或者stream_chat时,input_ids会被放到model.device上
        # 如果transformer.word_embeddings.device和model.device不同,则会导致RuntimeError
        # 因此这里将transformer.word_embeddings,transformer.final_layernorm,lm_head都放到第一张卡上
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
