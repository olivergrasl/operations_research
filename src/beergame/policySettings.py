from BPTK_Py import Module


class PolicySettings(Module):
    
    def __init__(self, model, name):
        super().__init__(model, name)

        self.gameModeOn = self.converter("gameModeOn")
        self.multiplayerModeOn = self.converter("multiplayerModeOn")
        self.sophisticatedOrderDecisionOn = self.converter("sophisticatedOrderDecisionOn")
        self.customOrderDecisionOn = self.converter("customOrderDecisionOn")
        self.includeSupplyLineOn = self.converter("includeSupplyLineOn")
        self.reIncludeBackorderOn = self.converter("reIncludeBackorderOn")
        self.steadyStateOn = self.converter("steadyStateOn")
        self.inventoryAdjustmentTime = self.converter("inventoryAdjustmentTime")
        self.targetInventory = self.converter("targetInventory")
        self.targetRetailerCost = self.converter("targetRetailerCost")
        self.targetSupplyChainCost = self.converter("targetSupplyChainCost")
        self.targetSupplyLineFactor = self.converter("targetSupplyLineFactor")
        self.targetSurplus = self.converter("targetSurplus")
        self.weightingBackorder = self.converter("weightingBackorder")
        self.weightingInventory = self.converter("weightingInventory")
        self.weightingOpenOrders = self.converter("weightingOpenOrders")

        # # Equations

        self.gameModeOn.equation = 0.0
        self.multiplayerModeOn.equation = 0.0
        self.sophisticatedOrderDecisionOn.equation = 0.0
        self.customOrderDecisionOn.equation = 0.0
        self.steadyStateOn.equation = 0.0
        self.inventoryAdjustmentTime.equation = 1.0
        self.includeSupplyLineOn.equation = 0.0
        self.reIncludeBackorderOn.equation = 0.0
        self.targetInventory.equation = 400.0
        self.targetRetailerCost.equation = 8200.0
        self.targetSupplyChainCost.equation = 31100.0
        self.targetSupplyLineFactor.equation = 1.0
        self.targetSurplus.equation = 400.0
        self.weightingBackorder.equation = 1.0
        self.weightingInventory.equation = 1.0
        self.weightingOpenOrders.equation = 1.0





