import random
import logging
import datetime
from locust import FastHttpUser, TaskSet, between
from faker import Faker

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

fake = Faker()

products = [
    '0PUK6V6EV0', '1YMWWN1N4O', '2ZYFJ3GM2N',
    '66VCHSJNUP', '6E92ZMYYFZ', '9SIQT8TOJO',
    'L9ECAV7KIM', 'LS4PSXUNUM', 'OLJCESPC7Z'
]

headers = {'Content-Type': 'application/x-www-form-urlencoded'}

def index(l):
    with l.client.get("/", headers=headers, catch_response=True) as res:
        if res.status_code != 200:
            logger.warning(f"GET / failed with status {res.status_code}")
            res.failure("Failed to load homepage")

def setCurrency(l):
    currency = random.choice(['EUR', 'USD', 'JPY', 'CAD', 'GBP', 'TRY'])
    with l.client.post("/setCurrency", {"currency_code": currency}, headers=headers, catch_response=True) as res:
        if res.status_code != 200:
            logger.warning(f"POST /setCurrency failed with status {res.status_code}")
            res.failure("Failed to set currency")

def browseProduct(l):
    product = random.choice(products)
    with l.client.get(f"/product/{product}", headers=headers, catch_response=True) as res:
        if res.status_code != 200:
            logger.warning(f"GET /product/{product} failed with status {res.status_code}")
            res.failure("Failed to load product page")

def viewCart(l):
    with l.client.get("/cart", headers=headers, catch_response=True) as res:
        if res.status_code != 200:
            logger.warning(f"GET /cart failed with status {res.status_code}")
            res.failure("Failed to view cart")

def addToCart(l):
    product = random.choice(products)
    with l.client.get(f"/product/{product}", headers=headers, catch_response=True):
        pass  # preload product page
    payload = {'product_id': product, 'quantity': random.randint(1, 10)}
    with l.client.post("/cart", data=payload, headers=headers, catch_response=True) as res:
        if res.status_code != 200:
            logger.warning(f"POST /cart failed with status {res.status_code}, data={payload}")
            res.failure("Failed to add to cart")

def empty_cart(l):
    with l.client.post("/cart/empty", headers=headers, catch_response=True) as res:
        if res.status_code != 200:
            logger.warning(f"POST /cart/empty failed with status {res.status_code}")
            res.failure("Failed to empty cart")

def checkout(l):
    addToCart(l)
    current_year = datetime.datetime.now().year + 1
    payload = {
        'email': fake.email(),
        'street_address': fake.street_address(),
        'zip_code': fake.zipcode(),
        'city': fake.city(),
        'state': fake.state_abbr(),
        'country': fake.country(),
        'credit_card_number': fake.credit_card_number(card_type="visa"),
        'credit_card_expiration_month': random.randint(1, 12),
        'credit_card_expiration_year': random.randint(current_year, current_year + 10),
        'credit_card_cvv': f"{random.randint(100, 999)}"
    }
    with l.client.post("/cart/checkout", data=payload, headers=headers, catch_response=True) as res:
        if res.status_code != 200:
            logger.warning(f"POST /cart/checkout failed with status {res.status_code}, payload={payload}")
            res.failure("Checkout failed")

def logout(l):
    with l.client.get("/logout", headers=headers, catch_response=True) as res:
        if res.status_code != 200:
            logger.warning(f"GET /logout failed with status {res.status_code}")
            res.failure("Logout failed")

class UserBehavior(TaskSet):
    def on_start(self):
        index(self)

    tasks = {
        index: 1,
        setCurrency: 2,
        browseProduct: 10,
        addToCart: 2,
        viewCart: 3,
        checkout: 1
    }

class WebsiteUser(FastHttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 10)
