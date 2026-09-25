from BPTK_Py import sd_functions as sd
from .supplyChainModule import SupplyChainModule


class Distributor(SupplyChainModule):
    def __init__(self, model,name):
        super().__init__(model, name)

    def initialize(self, supplier, customer, policySettings):
        super().initialize(supplier, customer, policySettings)

        
        
