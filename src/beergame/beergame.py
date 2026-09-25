from BPTK_Py import Model
from BPTK_Py import sd_functions as sd

from .brewery import Brewery
from .retailer import Retailer
from .wholesaler import Wholesaler
from .distributor import Distributor
from .performanceControlling import PerformanceControlling
from .policySettings import PolicySettings
from .supplyChainModule import SupplyChainModule

class Beergame(Model):
    def __init__(self):
        super().__init__(starttime=1.0,stoptime=24.0, dt=1.0, name="Beergame SD DSL")
        
         
        ####
        # Step 1: create the modules
        ####

        # the supply chain modules

        retailer = Retailer(
            model=self,
            name="retailer")

        wholesaler = Wholesaler(
            model=self,
            name="wholesaler")

        distributor = Distributor(
            model=self,
            name="distributor"
        )

        brewery = Brewery(
            model=self,
            name="brewery")
        
        # modules for settings and controlling
        
        policySettings = PolicySettings(
            model=self,
            name="policySettings"
        )

        performanceControlling = PerformanceControlling(
            model=self,
            name="performanceControlling"
        )

        
        ####
        # Step 2: initialize the modules
        ###
        retailer.initialize(supplier=wholesaler,customer=None,policySettings=policySettings)
        wholesaler.initialize(supplier=distributor, customer=retailer, policySettings=policySettings)
        distributor.initialize(supplier=brewery, customer=wholesaler, policySettings=policySettings)
        brewery.initialize(supplier=None, customer=distributor, policySettings=policySettings)
        performanceControlling.initialize(brewery=brewery,distributor=distributor,wholesaler=wholesaler,retailer=retailer,policySettings=policySettings)        




