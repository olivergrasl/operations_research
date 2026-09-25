from BPTK_Py import sd_functions as sd
from .supplyChainModule import SupplyChainModule


class Retailer(SupplyChainModule):
    def __init__(self, model,name):
        super().__init__(model, name)

    def initialize(self, supplier, customer, policySettings):
        super().initialize(supplier, customer, policySettings)
        self.dynamicCustomerOrder = self.converter("dynamicCustomerOrder")
        self.customerOrder = self.converter("customerOrder")

        self.points[self.fqn("dynamicCustomerOrder")] = [
            (1.0, 100.0), 
            (2.0, 400.0), 
            (3.0, 400.0), 
            (4.0, 400.0), 
            (5.0, 400.0), 
            (6.0, 400.0), 
            (7.0, 400.0), 
            (8.0, 400.0), 
            (9.0, 400.0), 
            (10.0, 400.0), 
            (11.0, 400.0), 
            (12.0, 400.0), 
            (13.0, 400.0), 
            (14.0, 400.0), 
            (15.0, 400.0), 
            (16.0, 400.0), 
            (17.0, 400.0), 
            (18.0, 400.0), 
            (19.0, 400.0), 
            (20.0, 400.0), 
            (21.0, 400.0), 
            (22.0, 400.0), 
            (23.0, 400.0), 
            (24.0, 400.0)
            ]
        
        self.dynamicCustomerOrder.equation = sd.lookup(sd.time(),self.fqn("dynamicCustomerOrder"))
        self.customerOrder.equation = policySettings.steadyStateOn * 100 + (1 - policySettings.steadyStateOn) * self.dynamicCustomerOrder
        self.incomingOrder.equation = self.customerOrder

        self.actualOrder.equation = policySettings.gameModeOn * self.order + (1 - policySettings.gameModeOn) * self.orderLine


