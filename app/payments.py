import braintree
from os import environ

gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        environment = braintree.Environment.Sandbox, # type: ignore
        merchant_id = environ["BRAINTREE_MERCHANT_ID"],
        public_key = environ["BRAINTREE_PUBLIC_KEY"],
        private_key = environ["BRAINTREE_PRIVATE_KEY"]
    )
)

def get_token(user_id):
    try:
        return gateway.client_token.generate({"customer_id": user_id})
    except:
        return gateway.client_token.generate()

def pay(cost: str, nonce: str):
    gateway.transaction.sale({
        "amount": cost,
        "payment_method_nonce": nonce,
        "options": {
            "submit_for_settlement": True
        }
    })