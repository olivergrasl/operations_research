from BPTK_Py import sd_functions as sd
from .supplyChainModule import SupplyChainModule


class Wholesaler(SupplyChainModule):
    def __init__(self, model,name):
        super().__init__(model, name)

    def initialize(self, supplier, customer, policySettings):
        super().initialize(supplier, customer, policySettings)
        self.deliveryDecision = self.converter("deliveryDecision")
        self.deliveryDecision.equation = sd.min(self.laggingBackorder + self.incomingOrder, self.laggingInventory + self.incomingDeliveryRate)
        self.outgoingDelivery.equation = self.deliveryDecision

         
        
    
