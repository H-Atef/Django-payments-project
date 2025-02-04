from abc import ABC,abstractmethod



class BasePaymentGateway(ABC):
    @abstractmethod
    def create_payment(self,request):
        pass
    @abstractmethod
    def payment_success(self,request):
        pass
    @abstractmethod
    def payment_cancel(self,request):
        pass
    @abstractmethod
    def payment_refund(self,request):
        pass
    @abstractmethod
    def payment_webhook(self,request):
        pass