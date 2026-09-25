from BPTK_Py import sd_functions as sd
from .supplyChainModule import SupplyChainModule


class Brewery(SupplyChainModule):
    def __init__(self, model,name):
        super().__init__(model, name)

    def initialize(self, supplier, customer, policySettings):
        super().initialize(supplier, customer, policySettings)
        self.actualProduction = self.converter("actualProduction")
        self.production = self.converter("production")
        self.production.equation = 100.0
        self.actualProduction.equation = policySettings.gameModeOn * (policySettings.multiplayerModeOn * self.production + (1 - policySettings.multiplayerModeOn) * self.orderLine) + (1 - policySettings.gameModeOn) * self.orderLine
        self.outgoingOrdersIn.equation = self.actualProduction
        self.orders.equation = self.actualProduction
        self.actualOrder.equation = 0.0
        self.incomingDelivery.equation = sd.delay(self.model, self.actualProduction, self.deliveryDelay, 100.0)

       
