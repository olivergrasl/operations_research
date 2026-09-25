from BPTK_Py import sd_functions as sd
from BPTK_Py import Module

class Floor(sd.Function):
    """
    Generic SD DSL function.
    """
    def __init__(self, element):
        self.element = element

    def term(self, time="t"):
        return "math.floor({})".format(self.element)


class SupplyChainModule(Module):
    def __init__(self, model, name):
        super().__init__(model, name)
        
        # Exports for supply chain
        self.actualOrder = self.converter("actualOrder")
        self.incomingOrder = self.converter("incomingOrder")
        self.sendingOrders = self.flow("sendingOrders")
        self.outgoingDelivery = self.converter("outgoingDelivery")
        self.outgoingDeliveryRate = self.flow("outgoingDeliveryRate")
        
        # Exports for performance controlling
        
        self.laggingInventory = self.stock("laggingInventory")
        self.laggingBackorder = self.converter("laggingBackorder")
        
        # Exports for subclasses
        self.deliveryDelay = self.converter("deliveryDelay")
        self.orderLine = self.stock("orderLine")
        self.orders = self.flow("orders")
        self.incomingDelivery = self.converter("incomingDelivery")
        self.incomingDeliveryRate = self.flow("incomingDeliveryRate")
        self.outgoingOrdersIn = self.flow("outgoingOrdersIn")
        self.order = self.converter("order")
        self.customOrder = self.converter("customOrder")
        self.sophisticatedOrderDecision = self.converter("sophisticatedOrderDecision")

    def initialize(self, supplier, customer, policySettings):
        # Stocks

        laggingSupplyLine = self.stock("laggingSupplyLine")
        incomingOrders = self.stock("incomingOrders")
        deliveries = self.stock("deliveries")
        outgoingOrders = self.stock("outgoingOrders")
        # Flows

        incomingOrderRate = self.flow("incomingOrderRate")
        makingOrders = self.flow("makingOrders")

        # # Converters

        totalOutgoingOrders = self.converter("totalOutgoingOrders")
        totalStock = self.converter("totalStock")
        targetTotalStock = self.converter("targetTotalStock")
        surplus = self.converter("surplus")
        laggingSurplus = self.converter("laggingSurplus")
        orderDecision = self.converter("orderDecision")
        naiveOrderDecision = self.converter("naiveOrderDecision")
        
        targetSupplyLine = self.converter("targetSupplyLine")

        openOrders = self.converter("openOrders")
        supplyLine = self.converter("supplyLine")
        orderDelay = self.converter("orderDelay")
        
        deliveryPolicy = self.converter("deliveryPolicy")
        
        expectedOrder = self.converter("expectedOrder")
        inventory = self.converter("inventory")
        backorder = self.converter("backorder")
        totalIncomingOrders = self.converter("totalIncomingOrders")
        
        orderFromOrderLine = self.converter("orderFromOrderLine")

        # # Initial Values
        
        laggingSupplyLine.initial_value = 100.0
        self.laggingInventory.initial_value = 400.0
        incomingOrders.initial_value = 0.0
        deliveries.initial_value = 0.0
        outgoingOrders.initial_value = 100.0
        self.orderLine.initial_value = 100.0

        

        self.order.equation = 100.0
        self.points[self.fqn("orderDelay")] = [
            (1.0, 1.0), 
            (2.0, 1.0), 
            (3.0, 1.0), 
            (4.0, 1.0), 
            (5.0, 1.0), 
            (6.0, 1.0), 
            (7.0, 1.0), 
            (8.0, 1.0), 
            (9.0, 1.0), 
            (10.0, 1.0), 
            (11.0, 1.0), 
            (12.0, 1.0), 
            (13.0, 1.0), 
            (14.0, 1.0), 
            (15.0, 1.0), 
            (16.0, 1.0), 
            (17.0, 1.0), 
            (18.0, 1.0), 
            (19.0, 1.0), 
            (20.0, 1.0), 
            (21.0, 1.0), 
            (22.0, 1.0), 
            (23.0, 1.0), 
            (24.0, 1.0)
        ]
        self.points[self.name+".deliveryDelay"] = [
            (1.0, 1.0),
            (2.0, 1.0), 
            (3.0, 1.0), 
            (4.0, 1.0), 
            (5.0, 1.0), 
            (6.0, 1.0), 
            (7.0, 1.0), 
            (8.0, 1.0), 
            (9.0, 1.0), 
            (10.0, 1.0), 
            (11.0, 1.0), 
            (12.0, 1.0), 
            (13.0, 1.0), 
            (14.0, 1.0), 
            (15.0, 1.0), 
            (16.0, 1.0), 
            (17.0, 1.0), 
            (18.0, 1.0), 
            (19.0, 1.0), 
            (20.0, 1.0), 
            (21.0, 1.0), 
            (22.0, 1.0), 
            (23.0, 1.0), 
            (24.0, 1.0)
        ]
        
        # # Equations

        orderDelay.equation = sd.lookup(sd.time(), self.fqn("orderDelay"))
        self.deliveryDelay.equation = sd.lookup(sd.time(), self.fqn("deliveryDelay"))
        makingOrders.equation = orderDecision
        self.orderLine.equation = makingOrders - self.sendingOrders
        self.laggingInventory.equation = self.incomingDeliveryRate - self.outgoingDeliveryRate
        deliveries.equation = self.outgoingDeliveryRate
        self.orders.equation = self.actualOrder
        openOrders.equation = supplyLine
        supplyLine.equation = self.orders + laggingSupplyLine - self.incomingDeliveryRate
        self.actualOrder.equation = policySettings.gameModeOn * (policySettings.multiplayerModeOn * self.order + (1 - policySettings.multiplayerModeOn) * self.orderLine) + (1 - policySettings.gameModeOn) * self.orderLine
        laggingSupplyLine.equation = self.orders - self.incomingDeliveryRate

        totalStock.equation = self.laggingInventory + laggingSupplyLine
        targetTotalStock.equation = targetSupplyLine + policySettings.targetInventory

        self.incomingOrder.equation = customer.actualOrder if customer is not None else None
        expectedOrder.equation = self.incomingOrder

        inventory.equation = sd.max(self.laggingInventory + self.incomingDeliveryRate - self.outgoingDeliveryRate, 0.0)
        
        surplus.equation = inventory - backorder
        laggingSurplus.equation = self.laggingInventory - self.laggingBackorder
        self.laggingBackorder.equation = sd.max(incomingOrders - deliveries, 0.0)
        backorder.equation = sd.max(self.laggingBackorder + incomingOrderRate - self.outgoingDeliveryRate, 0.0)

        incomingOrderRate.equation = self.incomingOrder
        incomingOrders.equation = incomingOrderRate
        totalIncomingOrders.equation = incomingOrders + incomingOrderRate
        self.outgoingOrdersIn.equation = self.actualOrder
        outgoingOrders.equation = self.outgoingOrdersIn
        totalOutgoingOrders.equation = self.outgoingOrdersIn + outgoingOrders
        
        self.incomingDelivery.equation = sd.delay(self.model, supplier.outgoingDeliveryRate, self.deliveryDelay, 100.0) if supplier is not None else None
        self.incomingDeliveryRate.equation = self.incomingDelivery

        deliveryPolicy.equation = sd.min(self.laggingBackorder + self.incomingOrder, self.laggingInventory + self.incomingDeliveryRate)
        self.outgoingDelivery.equation = deliveryPolicy
        self.outgoingDeliveryRate.equation = sd.min(self.laggingInventory + self.incomingDeliveryRate, self.outgoingDelivery) 

        orderFromOrderLine.equation = self.sendingOrders

        self.sendingOrders.equation = sd.delay(self.model, makingOrders, orderDelay, 100.0)
        
        targetSupplyLine.equation = policySettings.targetSupplyLineFactor * expectedOrder
        
        # ## Decision Policies

        # ### Order Decision

        orderDecision.equation = self.sophisticatedOrderDecision * policySettings.sophisticatedOrderDecisionOn + (1 - policySettings.sophisticatedOrderDecisionOn) * naiveOrderDecision

        # ### Naive Order Decision

        naiveOrderDecision.equation = sd.max(policySettings.weightingInventory * (policySettings.targetInventory - self.laggingInventory) + policySettings.weightingBackorder * self.laggingBackorder + expectedOrder, 0.0)

        # ### Sophisticated Order Decision

        self.sophisticatedOrderDecision.equation = sd.If(policySettings.customOrderDecisionOn,self.customOrder,sd.If(self.incomingOrder>100.0,sd.max(sd.round(self.incomingOrder + (policySettings.includeSupplyLineOn*(targetSupplyLine+policySettings.reIncludeBackorderOn*backorder-supplyLine) +policySettings.targetInventory - inventory) / policySettings.inventoryAdjustmentTime,0), 0.0),100.0))

        # default custom order

        self.points[self.fqn("customOrder")] = [
            (1.0, 100.0), 
            (2.0, 100.0), 
            (3.0, 100.0), 
            (4.0, 100.0), 
            (5.0, 100.0), 
            (6.0, 100.0), 
            (7.0, 100.0), 
            (8.0, 100.0), 
            (9.0, 100.0), 
            (10.0, 100.0), 
            (11.0, 100.0), 
            (12.0, 100.0), 
            (13.0, 100.0), 
            (14.0, 100.0), 
            (15.0, 100.0), 
            (16.0, 100.0), 
            (17.0, 100.0), 
            (18.0, 100.0), 
            (19.0, 100.0), 
            (20.0, 100.0), 
            (21.0, 100.0), 
            (22.0, 100.0), 
            (23.0, 100.0), 
            (24.0, 100.0)
            ]

        self.customOrder.equation=sd.lookup(sd.time(),self.fqn("customOrder"))













