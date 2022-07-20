from decouple import config
from pyot.conf.model import activate_model, ModelConf
from pyot.conf.pipeline import activate_pipeline, PipelineConf
API_KEY = config('API_KEY')

@activate_model("lol")
class LolModel(ModelConf):
    default_platform = 'euw1'
    default_region = 'europe'
    default_version = 'latest'
    default_locale = 'en_us'
    

    
@activate_pipeline("lol")
class LolPipeline(PipelineConf):
    name = "lol_main"
    default = True
    stores = [
        {
            "backend": "pyot.stores.riotapi.RiotAPI",
            "api_key": API_KEY,
            "rate_limiter": {
                "backend": "pyot.limiters.memory.MemoryLimiter",
                "limiting_share": 0.9,
             }
        }
    ]