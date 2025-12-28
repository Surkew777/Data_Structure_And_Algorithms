# =====================================================
# PROBLEM 1: PARKING LOT SYSTEM
# =====================================================

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional
from decimal import Decimal
import uuid

class VehicleType(Enum):
    MOTORCYCLE = "motorcycle"
    CAR = "car"
    BUS = "bus"

class SpotSize(Enum):
    SMALL = "small"    # Motorcycle
    MEDIUM = "medium"  # Car
    LARGE = "large"    # Bus

class SpotStatus(Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    RESERVED = "reserved"

class Vehicle:
    def __init__(self, license_plate: str, vehicle_type: VehicleType):
        self.license_plate = license_plate
        self.vehicle_type = vehicle_type
    
    def can_fit_in_spot(self, spot_size: SpotSize) -> bool:
        size_mapping = {
            VehicleType.MOTORCYCLE: [SpotSize.SMALL, SpotSize.MEDIUM, SpotSize.LARGE],
            VehicleType.CAR: [SpotSize.MEDIUM, SpotSize.LARGE],
            VehicleType.BUS: [SpotSize.LARGE]
        }
        return spot_size in size_mapping[self.vehicle_type]

class ParkingSpot:
    def __init__(self, spot_id: str, spot_size: SpotSize, floor: int):
        self.spot_id = spot_id
        self.spot_size = spot_size
        self.floor = floor
        self.status = SpotStatus.AVAILABLE
        self.parked_vehicle: Optional[Vehicle] = None
        self.parked_time: Optional[datetime] = None
    
    def park_vehicle(self, vehicle: Vehicle) -> bool:
        if (self.status == SpotStatus.AVAILABLE and 
            vehicle.can_fit_in_spot(self.spot_size)):
            self.status = SpotStatus.OCCUPIED
            self.parked_vehicle = vehicle
            self.parked_time = datetime.now()
            return True
        return False
    
    def remove_vehicle(self) -> Optional[Vehicle]:
        if self.status == SpotStatus.OCCUPIED:
            vehicle = self.parked_vehicle
            self.parked_vehicle = None
            self.parked_time = None
            self.status = SpotStatus.AVAILABLE
            return vehicle
        return None

class ParkingTicket:
    def __init__(self, ticket_id: str, vehicle: Vehicle, spot: ParkingSpot):
        self.ticket_id = ticket_id
        self.vehicle = vehicle
        self.spot = spot
        self.entry_time = datetime.now()
        self.exit_time: Optional[datetime] = None
        self.amount_paid: Optional[Decimal] = None
    
    def complete_payment(self, amount: Decimal):
        self.amount_paid = amount
        self.exit_time = datetime.now()

class ParkingRateCalculator:
    def __init__(self):
        self.hourly_rates = {
            VehicleType.MOTORCYCLE: Decimal('2.00'),
            VehicleType.CAR: Decimal('5.00'),
            VehicleType.BUS: Decimal('10.00')
        }
    
    def calculate_fee(self, vehicle_type: VehicleType, hours_parked: float) -> Decimal:
        rate = self.hourly_rates[vehicle_type]
        return rate * Decimal(str(hours_parked)).quantize(Decimal('0.01'))

class ParkingLot:
    def __init__(self, name: str, total_floors: int):
        self.name = name
        self.total_floors = total_floors
        self.spots: Dict[str, ParkingSpot] = {}
        self.active_tickets: Dict[str, ParkingTicket] = {}
        self.completed_tickets: List[ParkingTicket] = []
        self.rate_calculator = ParkingRateCalculator()
    
    def add_spot(self, spot: ParkingSpot):
        self.spots[spot.spot_id] = spot
    
    def find_available_spot(self, vehicle: Vehicle) -> Optional[ParkingSpot]:
        for spot in self.spots.values():
            if (spot.status == SpotStatus.AVAILABLE and 
                vehicle.can_fit_in_spot(spot.spot_size)):
                return spot
        return None
    
    def park_vehicle(self, vehicle: Vehicle) -> Optional[ParkingTicket]:
        spot = self.find_available_spot(vehicle)
        if spot and spot.park_vehicle(vehicle):
            ticket_id = str(uuid.uuid4())
            ticket = ParkingTicket(ticket_id, vehicle, spot)
            self.active_tickets[ticket_id] = ticket
            return ticket
        return None
    
    def exit_vehicle(self, ticket_id: str) -> Optional[Decimal]:
        if ticket_id in self.active_tickets:
            ticket = self.active_tickets[ticket_id]
            vehicle = ticket.spot.remove_vehicle()
            
            if vehicle:
                # Calculate fee
                hours_parked = (datetime.now() - ticket.entry_time).total_seconds() / 3600
                fee = self.rate_calculator.calculate_fee(vehicle.vehicle_type, hours_parked)
                
                ticket.complete_payment(fee)
                self.completed_tickets.append(ticket)
                del self.active_tickets[ticket_id]
                
                return fee
        return None
    
    def get_availability_report(self) -> Dict[str, int]:
        report = {}
        for size in SpotSize:
            available = sum(1 for spot in self.spots.values() 
                          if spot.spot_size == size and spot.status == SpotStatus.AVAILABLE)
            occupied = sum(1 for spot in self.spots.values() 
                         if spot.spot_size == size and spot.status == SpotStatus.OCCUPIED)
            report[size.value] = {"available": available, "occupied": occupied}
        return report

# =====================================================
# PROBLEM 2: SOCIAL MEDIA PLATFORM
# =====================================================

class PrivacyLevel(Enum):
    PUBLIC = "public"
    FRIENDS_ONLY = "friends_only"
    PRIVATE = "private"

class PostType(Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"

class User:
    def __init__(self, user_id: str, username: str, email: str):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.followers: List['User'] = []
        self.following: List['User'] = []
        self.posts: List['Post'] = []
        self.privacy_level = PrivacyLevel.PUBLIC
        self.created_at = datetime.now()
    
    def follow(self, user: 'User') -> bool:
        if user not in self.following and user != self:
            self.following.append(user)
            user.followers.append(self)
            return True
        return False
    
    def unfollow(self, user: 'User') -> bool:
        if user in self.following:
            self.following.remove(user)
            user.followers.remove(self)
            return True
        return False
    
    def create_post(self, content: str, post_type: PostType = PostType.TEXT) -> 'Post':
        post = Post(str(uuid.uuid4()), self, content, post_type)
        self.posts.append(post)
        return post
    
    def can_view_post(self, post: 'Post') -> bool:
        if post.author == self:
            return True
        if post.privacy_level == PrivacyLevel.PUBLIC:
            return True
        if post.privacy_level == PrivacyLevel.FRIENDS_ONLY:
            return self in post.author.followers
        return False

class Post:
    def __init__(self, post_id: str, author: User, content: str, post_type: PostType):
        self.post_id = post_id
        self.author = author
        self.content = content
        self.post_type = post_type
        self.privacy_level = author.privacy_level
        self.likes: List[User] = []
        self.comments: List['Comment'] = []
        self.created_at = datetime.now()
    
    def like(self, user: User) -> bool:
        if user not in self.likes and user.can_view_post(self):
            self.likes.append(user)
            return True
        return False
    
    def unlike(self, user: User) -> bool:
        if user in self.likes:
            self.likes.remove(user)
            return True
        return False
    
    def add_comment(self, user: User, content: str) -> Optional['Comment']:
        if user.can_view_post(self):
            comment = Comment(str(uuid.uuid4()), user, content, self)
            self.comments.append(comment)
            return comment
        return None
    
    def get_like_count(self) -> int:
        return len(self.likes)

class Comment:
    def __init__(self, comment_id: str, author: User, content: str, post: Post):
        self.comment_id = comment_id
        self.author = author
        self.content = content
        self.post = post
        self.likes: List[User] = []
        self.created_at = datetime.now()
    
    def like(self, user: User):
        if user not in self.likes:
            self.likes.append(user)
    
    def unlike(self, user: User):
        if user in self.likes:
            self.likes.remove(user)

class SocialMediaPlatform:
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.posts: Dict[str, Post] = {}
    
    def register_user(self, username: str, email: str) -> User:
        user_id = str(uuid.uuid4())
        user = User(user_id, username, email)
        self.users[user_id] = user
        return user
    
    def get_user_feed(self, user: User, limit: int = 20) -> List[Post]:
        feed_posts = []
        for followed_user in user.following:
            for post in followed_user.posts:
                if user.can_view_post(post):
                    feed_posts.append(post)
        
        # Sort by creation time (newest first)
        feed_posts.sort(key=lambda p: p.created_at, reverse=True)
        return feed_posts[:limit]

# =====================================================
# PROBLEM 3: E-COMMERCE SYSTEM
# =====================================================

class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class PaymentStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class PaymentMethod(Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"

class Category:
    def __init__(self, category_id: str, name: str, parent: Optional['Category'] = None):
        self.category_id = category_id
        self.name = name
        self.parent = parent
        self.subcategories: List['Category'] = []
        self.products: List['Product'] = []
    
    def add_subcategory(self, subcategory: 'Category'):
        subcategory.parent = self
        self.subcategories.append(subcategory)

class Product:
    def __init__(self, product_id: str, name: str, price: Decimal, category: Category):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.category = category
        self.description = ""
        self.stock_quantity = 0
        self.is_active = True
        self.created_at = datetime.now()
        category.products.append(self)
    
    def update_stock(self, quantity: int):
        self.stock_quantity = max(0, self.stock_quantity + quantity)
    
    def is_in_stock(self, quantity: int = 1) -> bool:
        return self.stock_quantity >= quantity

class CartItem:
    def __init__(self, product: Product, quantity: int):
        self.product = product
        self.quantity = quantity
        self.unit_price = product.price
    
    def get_total_price(self) -> Decimal:
        return self.unit_price * self.quantity

class ShoppingCart:
    def __init__(self, customer: 'Customer'):
        self.customer = customer
        self.items: List[CartItem] = []
        self.created_at = datetime.now()
    
    def add_item(self, product: Product, quantity: int) -> bool:
        if product.is_in_stock(quantity):
            # Check if item already exists
            for item in self.items:
                if item.product.product_id == product.product_id:
                    item.quantity += quantity
                    return True
            
            # Add new item
            self.items.append(CartItem(product, quantity))
            return True
        return False
    
    def remove_item(self, product_id: str):
        self.items = [item for item in self.items if item.product.product_id != product_id]
    
    def get_total(self) -> Decimal:
        return sum(item.get_total_price() for item in self.items)
    
    def clear(self):
        self.items = []

class Customer:
    def __init__(self, customer_id: str, name: str, email: str, address: str):
        self.customer_id = customer_id
        self.name = name
        self.email = email
        self.address = address
        self.orders: List['Order'] = []
        self.cart = ShoppingCart(self)

class Order:
    def __init__(self, order_id: str, customer: Customer, items: List[CartItem]):
        self.order_id = order_id
        self.customer = customer
        self.items = items.copy()
        self.status = OrderStatus.PENDING
        self.total_amount = sum(item.get_total_price() for item in items)
        self.created_at = datetime.now()
        self.payment: Optional['Payment'] = None
        customer.orders.append(self)
    
    def confirm(self):
        self.status = OrderStatus.CONFIRMED
    
    def ship(self):
        if self.status == OrderStatus.CONFIRMED:
            self.status = OrderStatus.SHIPPED
    
    def deliver(self):
        if self.status == OrderStatus.SHIPPED:
            self.status = OrderStatus.DELIVERED
    
    def cancel(self):
        if self.status in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
            self.status = OrderStatus.CANCELLED

class Payment:
    def __init__(self, payment_id: str, order: Order, amount: Decimal, method: PaymentMethod):
        self.payment_id = payment_id
        self.order = order
        self.amount = amount
        self.method = method
        self.status = PaymentStatus.PENDING
        self.created_at = datetime.now()
        order.payment = self
    
    def process(self) -> bool:
        # Simulate payment processing
        self.status = PaymentStatus.COMPLETED
        return True

class InventoryManager:
    def __init__(self):
        self.products: Dict[str, Product] = {}
    
    def add_product(self, product: Product):
        self.products[product.product_id] = product
    
    def update_stock(self, product_id: str, quantity: int):
        if product_id in self.products:
            self.products[product_id].update_stock(quantity)
    
    def reserve_stock(self, product_id: str, quantity: int) -> bool:
        if product_id in self.products:
            product = self.products[product_id]
            if product.is_in_stock(quantity):
                product.update_stock(-quantity)
                return True
        return False

class ECommerceSystem:
    def __init__(self):
        self.customers: Dict[str, Customer] = {}
        self.orders: Dict[str, Order] = {}
        self.products: Dict[str, Product] = {}
        self.categories: Dict[str, Category] = {}
        self.inventory_manager = InventoryManager()
    
    def create_customer(self, name: str, email: str, address: str) -> Customer:
        customer_id = str(uuid.uuid4())
        customer = Customer(customer_id, name, email, address)
        self.customers[customer_id] = customer
        return customer
    
    def create_order(self, customer: Customer) -> Optional[Order]:
        if customer.cart.items:
            order_id = str(uuid.uuid4())
            order = Order(order_id, customer, customer.cart.items)
            self.orders[order_id] = order
            
            # Reserve stock
            for item in order.items:
                self.inventory_manager.reserve_stock(
                    item.product.product_id, 
                    item.quantity
                )
            
            customer.cart.clear()
            return order
        return None

# =====================================================
# PROBLEM 4: GAME DEVELOPMENT (RPG SYSTEM)
# =====================================================

class CharacterClass(Enum):
    WARRIOR = "warrior"
    MAGE = "mage"
    ARCHER = "archer"
    ROGUE = "rogue"

class ItemType(Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    POTION = "potion"
    CONSUMABLE = "consumable"

class QuestStatus(Enum):
    AVAILABLE = "available"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"

class Stat:
    def __init__(self, base_value: int):
        self.base_value = base_value
        self.bonus = 0
    
    @property
    def total(self) -> int:
        return self.base_value + self.bonus

class CharacterStats:
    def __init__(self, strength: int, intelligence: int, agility: int, vitality: int):
        self.strength = Stat(strength)
        self.intelligence = Stat(intelligence)
        self.agility = Stat(agility)
        self.vitality = Stat(vitality)
    
    def apply_bonuses(self, stat_bonuses: Dict[str, int]):
        for stat_name, bonus in stat_bonuses.items():
            if hasattr(self, stat_name):
                getattr(self, stat_name).bonus += bonus

class Item:
    def __init__(self, item_id: str, name: str, item_type: ItemType, value: int):
        self.item_id = item_id
        self.name = name
        self.item_type = item_type
        self.value = value
        self.stat_bonuses: Dict[str, int] = {}
    
    def use(self, character: 'Character') -> bool:
        if self.item_type == ItemType.POTION:
            character.heal(self.value)
            return True
        return False

class Weapon(Item):
    def __init__(self, item_id: str, name: str, damage: int, required_level: int = 1):
        super().__init__(item_id, name, ItemType.WEAPON, damage)
        self.damage = damage
        self.required_level = required_level

class Armor(Item):
    def __init__(self, item_id: str, name: str, defense: int, required_level: int = 1):
        super().__init__(item_id, name, ItemType.ARMOR, defense)
        self.defense = defense
        self.required_level = required_level

class Inventory:
    def __init__(self, capacity: int = 50):
        self.capacity = capacity
        self.items: List[Item] = []
    
    def add_item(self, item: Item) -> bool:
        if len(self.items) < self.capacity:
            self.items.append(item)
            return True
        return False
    
    def remove_item(self, item_id: str) -> Optional[Item]:
        for i, item in enumerate(self.items):
            if item.item_id == item_id:
                return self.items.pop(i)
        return None
    
    def get_items_by_type(self, item_type: ItemType) -> List[Item]:
        return [item for item in self.items if item.item_type == item_type]

class Character:
    def __init__(self, character_id: str, name: str, character_class: CharacterClass):
        self.character_id = character_id
        self.name = name
        self.character_class = character_class
        self.level = 1
        self.experience = 0
        self.experience_to_next_level = 100
        
        # Initialize stats based on class
        self.stats = self._initialize_stats()
        self.max_health = self.stats.vitality.total * 10
        self.current_health = self.max_health
        self.max_mana = self.stats.intelligence.total * 5
        self.current_mana = self.max_mana
        
        self.inventory = Inventory()
        self.equipped_weapon: Optional[Weapon] = None
        self.equipped_armor: Optional[Armor] = None
        self.active_quests: List['Quest'] = []
        self.completed_quests: List['Quest'] = []
    
    def _initialize_stats(self) -> CharacterStats:
        base_stats = {
            CharacterClass.WARRIOR: CharacterStats(15, 8, 10, 12),
            CharacterClass.MAGE: CharacterStats(8, 15, 10, 10),
            CharacterClass.ARCHER: CharacterStats(10, 10, 15, 10),
            CharacterClass.ROGUE: CharacterStats(12, 10, 15, 8)
        }
        return base_stats[self.character_class]
    
    def gain_experience(self, exp: int):
        self.experience += exp
        while self.experience >= self.experience_to_next_level:
            self.level_up()
    
    def level_up(self):
        self.level += 1
        self.experience -= self.experience_to_next_level
        self.experience_to_next_level = int(self.experience_to_next_level * 1.5)
        
        # Increase stats
        self.stats.strength.base_value += 2
        self.stats.intelligence.base_value += 2
        self.stats.agility.base_value += 2
        self.stats.vitality.base_value += 2
        
        # Update health and mana
        old_max_health = self.max_health
        old_max_mana = self.max_mana
        self.max_health = self.stats.vitality.total * 10
        self.max_mana = self.stats.intelligence.total * 5
        
        # Heal proportionally
        self.current_health += (self.max_health - old_max_health)
        self.current_mana += (self.max_mana - old_max_mana)
    
    def equip_weapon(self, weapon: Weapon) -> bool:
        if weapon in self.inventory.items and self.level >= weapon.required_level:
            if self.equipped_weapon:
                self.stats.apply_bonuses({"strength": -self.equipped_weapon.damage})
            
            self.equipped_weapon = weapon
            self.stats.apply_bonuses({"strength": weapon.damage})
            return True
        return False
    
    def attack(self, target: 'Character') -> int:
        base_damage = self.stats.strength.total
        if self.equipped_weapon:
            base_damage += self.equipped_weapon.damage
        
        # Apply target's defense
        defense = target.stats.vitality.total
        if target.equipped_armor:
            defense += target.equipped_armor.defense
        
        damage = max(1, base_damage - defense)
        target.take_damage(damage)
        return damage
    
    def take_damage(self, damage: int):
        self.current_health = max(0, self.current_health - damage)
    
    def heal(self, amount: int):
        self.current_health = min(self.max_health, self.current_health + amount)
    
    def is_alive(self) -> bool:
        return self.current_health > 0
    
    def accept_quest(self, quest: 'Quest') -> bool:
        if quest.is_available() and self.level >= quest.required_level:
            quest.status = QuestStatus.ACTIVE
            self.active_quests.append(quest)
            return True
        return False
    
    def complete_quest(self, quest: 'Quest') -> bool:
        if quest in self.active_quests and quest.is_completed():
            self.active_quests.remove(quest)
            self.completed_quests.append(quest)
            
            # Reward experience
            self.gain_experience(quest.experience_reward)
            
            # Reward items
            for item in quest.item_rewards:
                self.inventory.add_item(item)
            
            return True
        return False

class Quest:
    def __init__(self, quest_id: str, name: str, description: str, required_level: int):
        self.quest_id = quest_id
        self.name = name
        self.description = description
        self.required_level = required_level
        self.status = QuestStatus.AVAILABLE
        self.experience_reward = 0
        self.item_rewards: List[Item] = []
        self.objectives: List[str] = []
        self.completed_objectives: List[str] = []
    
    def is_available(self) -> bool:
        return self.status == QuestStatus.AVAILABLE
    
    def is_completed(self) -> bool:
        return len(self.completed_objectives) == len(self.objectives)
    
    def complete_objective(self, objective: str):
        if objective in self.objectives and objective not in self.completed_objectives:
            self.completed_objectives.append(objective)
            
            if self.is_completed():
                self.status = QuestStatus.COMPLETED

class GameWorld:
    def __init__(self):
        self.characters: Dict[str, Character] = {}
        self.quests: Dict[str, Quest] = {}
        self.items: Dict[str, Item] = {}
    
    def create_character(self, name: str, character_class: CharacterClass) -> Character:
        character_id = str(uuid.uuid4())
        character = Character(character_id, name, character_class)
        self.characters[character_id] = character
        return character
    
    def create_quest(self, name: str, description: str, required_level: int) -> Quest:
        quest_id = str(uuid.uuid4())
        quest = Quest(quest_id, name, description, required_level)
        self.quests[quest_id] = quest
        return quest
    
    def initiate_combat(self, attacker: Character, defender: Character) -> str:
        if not attacker.is_alive() or not defender.is_alive():
            return "Combat cannot proceed - one or both characters are dead"
        
        damage = attacker.attack(defender)
        result = f"{attacker.name} attacks {defender.name} for {damage} damage"
        
        if not defender.is_alive():
            result += f"\n{defender.name} has been defeated!"
            attacker.gain_experience(defender.level * 50)
        
        return result

# =====================================================
# PROBLEM 5: CALENDAR SYSTEM
# =====================================================

class EventType(Enum):
    MEETING = "meeting"
    APPOINTMENT = "appointment"
    REMINDER = "reminder"
    TASK = "task"
    HOLIDAY = "holiday"

class RecurrenceType(Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

class EventStatus(Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class CalendarUser:
    def __init__(self, user_id: str, name: str, email: str, timezone: str = "UTC"):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.timezone = timezone
        self.calendars: List['Calendar'] = []

class Event:
    def __init__(self, event_id: str, title: str, start_time: datetime, end_time: datetime, 
                 event_type: EventType = EventType.MEETING):
        self.event_id = event_id
        self.title = title
        self.description = ""
        self.start_time = start_time
        self.end_time = end_time
        self.event_type = event_type
        self.status = EventStatus.SCHEDULED
        self.location = ""
        self.attendees: List[CalendarUser] = []
        self.creator: Optional[CalendarUser] = None
        self.recurrence_type = RecurrenceType.NONE
        self.recurrence_end_date: Optional[datetime] = None
        self.reminders: List[int] = []  # Minutes before event
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def add_attendee(self, user: CalendarUser):
        if user not in self.attendees:
            self.attendees.append(user)
    
    def remove_attendee(self, user: CalendarUser):
        if user in self.attendees:
            self.attendees.remove(user)
    
    def update_status(self, status: EventStatus):
        self.status = status
        self.updated_at = datetime.now()
    
    def is_recurring(self) -> bool:
        return self.recurrence_type != RecurrenceType.NONE
    
    def get_duration_minutes(self) -> int:
        return int((self.end_time - self.start_time).total_seconds() / 60)
    
    def conflicts_with(self, other_event: 'Event') -> bool:
        return (self.start_time < other_event.end_time and 
                self.end_time > other_event.start_time)

class Calendar:
    def __init__(self, calendar_id: str, name: str, owner: CalendarUser):
        self.calendar_id = calendar_id
        self.name = name
        self.owner = owner
        self.events: Dict[str, Event] = {}
        self.shared_users: List[CalendarUser] = []
        self.is_public = False
        self.color = "#3498db"  # Default blue
        owner.calendars.append(self)
    
    