from BPTK_Py import sd_functions as sd
from BPTK_Py import Module


class PerformanceControlling(Module):

    def __init__(self, model,name):
        super().__init__(model,name)

    def initialize(self,brewery, distributor, wholesaler, retailer, policySettings):
        # # Stocks

        supplyChainCostAccLagging = self.stock("supplyChainCostAccLagging")
        breweryCostAccLagging = self.stock("breweryCostAccLagging")
        distributorCostAccLagging = self.stock("distributorCostAccLagging")
        wholesalerCostAccLagging = self.stock("wholesalerCostAccLagging")
        retailerCostAccLagging = self.stock("retailerCostAccLagging")

        # # Flows

        accSupplyChainCost = self.flow("accSupplyChainCost")
        breweryCostIn = self.flow("breweryCostIn")
        distributorCostIn = self.flow("distributorCostIn")
        wholesalerCostIn = self.flow("wholesalerCostIn")
        retailerCostIn = self.flow("retailerCostIn")

        # # Converters

        # ## Brewery

        breweryCost = self.converter("breweryCost")
        breweryBackorderCost = self.converter("breweryBackorderCost")
        breweryInventoryCost = self.converter("breweryInventoryCost")
        breweryCostAcc = self.converter("breweryCostAcc")


        # ## Distributor

        distributorCost = self.converter("distributorCost")
        distributorBackorderCost = self.converter("distributorBackorderCost")
        distributorInventoryCost = self.converter("distributorInventoryCost")
        distributorCostAcc = self.converter("distributorCostAcc")

        # ## Wholesaler

        wholesalerCost = self.converter("wholesalerCost")
        wholesalerBackorderCost = self.converter("wholesalerBackorderCost")
        wholesalerInventoryCost = self.converter("wholesalerInventoryCost")
        wholesalerCostAcc = self.converter("wholesalerCostAcc")

        # ## Retailer

        retailerCost = self.converter("retailerCost")
        retailerBackorderCost = self.converter("retailerBackorderCost")
        retailerInventoryCost = self.converter("retailerInventoryCost")
        retailerCostAcc = self.converter("retailerCostAcc")

        # ## Supply Chain

        supplyChainCost = self.converter("supplyChainCost")
        supplyChainCostAcc = self.converter("supplyChainCostAcc")

        # # Constants

        # ## Supply Chain

        costPerItemInBackorder = self.converter("costPerItemInBackorder")
        costPerItemInInventory = self.converter("costPerItemInInventory")


        ## Initial values
        supplyChainCostAccLagging.initial_value = 0.0
        breweryCostAccLagging.initial_value = 0.0
        distributorCostAccLagging.initial_value = 0.0
        wholesalerCostAccLagging.initial_value = 0.0
        retailerCostAccLagging.initial_value = 0.0

        # # Equations

        # ## Supply Chain

        costPerItemInInventory.equation = 0.5
        costPerItemInBackorder.equation = 1.0

        supplyChainCost.equation = breweryCost + retailerCost + distributorCost +wholesalerCost
        accSupplyChainCost.equation = supplyChainCost
        supplyChainCostAccLagging.equation = accSupplyChainCost 
        supplyChainCostAcc.equation = accSupplyChainCost + supplyChainCostAccLagging

        # ## Brewery*

        breweryCost.equation = breweryBackorderCost + breweryInventoryCost
        breweryBackorderCost.equation = costPerItemInBackorder * brewery.laggingBackorder
        breweryInventoryCost.equation = costPerItemInInventory * sd.max(brewery.laggingInventory, policySettings.targetInventory)
        breweryCostIn.equation = breweryCost
        breweryCostAccLagging.equation = breweryCostIn
        breweryCostAcc.equation = breweryCostIn + breweryCostAccLagging

        # ## Distributor

        distributorCost.equation = distributorBackorderCost + distributorInventoryCost
        distributorBackorderCost.equation = costPerItemInBackorder * distributor.laggingBackorder
        distributorInventoryCost.equation = costPerItemInInventory * sd.max(distributor.laggingInventory, policySettings.targetInventory)
        distributorCostIn.equation = distributorCost
        distributorCostAccLagging.equation = distributorCostIn
        distributorCostAcc.equation = distributorCostIn + distributorCostAccLagging

        # ## Wholesaler

        wholesalerCost.equation = wholesalerBackorderCost + wholesalerInventoryCost
        wholesalerBackorderCost.equation = costPerItemInBackorder * wholesaler.laggingBackorder
        wholesalerInventoryCost.equation = costPerItemInInventory * sd.max(wholesaler.laggingInventory, policySettings.targetInventory )
        wholesalerCostIn.equation = wholesalerCost
        wholesalerCostAccLagging.equation = wholesalerCostIn
        wholesalerCostAcc.equation = wholesalerCostIn + wholesalerCostAccLagging

        # ## Retailer

        retailerCost.equation = retailerBackorderCost + retailerInventoryCost
        retailerBackorderCost.equation = costPerItemInBackorder * retailer.laggingBackorder
        retailerInventoryCost.equation = costPerItemInInventory * sd.max(retailer.laggingInventory, policySettings.targetInventory )
        retailerCostIn.equation = retailerCost
        retailerCostAccLagging.equation = retailerCostIn
        retailerCostAcc.equation = retailerCostIn + retailerCostAccLagging