def effective_price(price, discount, delivery):
    return round(price - (price * discount / 100) + delivery, 2)

def pricewise_score(price, rating, discount):
    # Transparent demo score: lower price + rating + discount.
    rating_part = min(max(rating / 5 * 20, 0), 20)
    discount_part = min(max(discount, 0), 20)
    price_part = max(0, 60 - price / 2000)
    return round(min(price_part + rating_part + discount_part, 100), 1)
