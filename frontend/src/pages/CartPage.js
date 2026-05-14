import React, { useState } from 'react';
import { useApp } from '../context/AppContext';

const CartPage = () => {
  const { cart, handleRemoveFromCart, user, setPage, selectedCurrency,
    currencies, shippingZones } = useApp();
  const [checkoutMode, setCheckoutMode] = useState(false);

  const currencySymbol = currencies.find(c => c.code === selectedCurrency)?.symbol || '$';

  const CheckoutForm = () => (
    <div className="checkout-form">
      <h3>Shipping Details</h3>
      <div className="form-grid">
        <div className="form-field">
          <label>Full Name</label>
          <input type="text" defaultValue={user?.name || ''} placeholder="John Doe" />
        </div>
        <div className="form-field">
          <label>Email</label>
          <input type="email" defaultValue={user?.email || ''} placeholder="john@example.com" />
        </div>
        <div className="form-field full-width">
          <label>Street Address</label>
          <input type="text" placeholder="123 Main St, Apt 4B" />
        </div>
        <div className="form-field">
          <label>City</label>
          <input type="text" placeholder="New York" />
        </div>
        <div className="form-field">
          <label>State/Province</label>
          <input type="text" placeholder="NY" />
        </div>
        <div className="form-field">
          <label>Postal Code</label>
          <input type="text" placeholder="10001" />
        </div>
        <div className="form-field">
          <label>Country</label>
          <select defaultValue="US">
            <option value="US">United States</option>
            <option value="GB">United Kingdom</option>
            <option value="DE">Germany</option>
            <option value="FR">France</option>
            <option value="IN">India</option>
            <option value="SG">Singapore</option>
            <option value="AU">Australia</option>
            <option value="JP">Japan</option>
            <option value="AE">UAE</option>
            <option value="BR">Brazil</option>
            <option value="NG">Nigeria</option>
            <option value="ZA">South Africa</option>
          </select>
        </div>
        <div className="form-field">
          <label>Payment Method</label>
          <select defaultValue="card">
            <option value="card">Credit/Debit Card</option>
            <option value="paypal">PayPal</option>
            <option value="stripe">Stripe</option>
            <option value="cod">Cash on Delivery</option>
          </select>
        </div>
      </div>
      <div className="shipping-zones-info">
        <h4>Worldwide Shipping Available</h4>
        <div className="zones-grid">
          {shippingZones.map(z => (
            <div key={z.id} className="zone-badge" title={z.description}>
              <strong>{z.name}</strong>
              <span>{z.estimated_days_min}-{z.estimated_days_max} days</span>
              <span>{currencySymbol}{z.base_rate.toFixed(2)} + {currencySymbol}{z.rate_per_kg.toFixed(2)}/kg</span>
            </div>
          ))}
        </div>
      </div>
      <button className="btn btn-primary btn-lg" style={{ width: '100%', marginTop: 16 }}
        onClick={async () => {
          try {
            const { api } = await import('../api');
            const order = await api('/api/store/checkout?user_id=1', {
              method: 'POST',
              body: JSON.stringify({
                payment_method: 'card',
                currency: selectedCurrency,
                shipping_address: {
                  full_name: user?.name || 'Reader',
                  street: '123 Main St',
                  city: 'New York',
                  postal_code: '10001',
                  country: 'US',
                },
              }),
            });
            const { toast } = await import('react-toastify');
            toast(`Order placed! #${order.order_number}`, { type: 'success' });
            setPage('orders');
          } catch (e) {
            const { toast } = await import('react-toastify');
            toast(e.message, { type: 'error' });
          }
        }}>
        Place Order
      </button>
      <button className="btn btn-outline" style={{ width: '100%', marginTop: 8 }}
        onClick={() => setCheckoutMode(false)}>
        Back to Cart
      </button>
    </div>
  );

  if (checkoutMode) return <div className="page page-3d"><div className="page-header"><h1 className="page-title text-3d-strong">Checkout</h1></div><CheckoutForm /></div>;

  return (
    <div className="page page-3d">
      <div className="page-header">
        <h1 className="page-title text-3d-strong">Shopping <span>Cart</span></h1>
      </div>
      {cart.items.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">🛒</div>
          <h3>Your Cart is Empty</h3>
          <p>Browse the Library and add books to your cart</p>
          <button className="btn btn-primary" style={{ marginTop: 16 }} onClick={() => setPage('library')}>
            Browse Books
          </button>
        </div>
      ) : (
        <>
          <div className="cart-items">
            {cart.items.map(item => (
              <div key={item.id} className="card cart-item card-3d-tilt">
                {item.book?.images?.[0] && (
                  <img src={item.book.images[0].url} alt={item.book.title} className="cart-cover" />
                )}
                <div className="cart-item-info">
                  <h3>{item.book?.title || 'Book'}</h3>
                  <p className="book-author">{item.book?.author}</p>
                  <p className="price-tag" style={{ fontSize: 18 }}>
                    {currencySymbol}{(item.book?.price || 0).toFixed(2)}
                  </p>
                </div>
                <div className="cart-item-actions">
                  <span className="badge badge-info">Qty: {item.quantity}</span>
                  <button className="btn btn-sm btn-danger"
                    onClick={() => handleRemoveFromCart(item.id)}>
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>
          <div className="card cart-summary">
            <div className="cart-summary-row">
              <span>Subtotal ({cart.total_items} items)</span>
              <span>{currencySymbol}{cart.subtotal.toFixed(2)}</span>
            </div>
            <div className="cart-summary-row">
              <span>Shipping</span>
              <span>Calculated at checkout</span>
            </div>
            <div className="cart-summary-row">
              <span>Currency</span>
              <span>{selectedCurrency}</span>
            </div>
            <div className="cart-summary-row total">
              <span>Total</span>
              <span>{currencySymbol}{cart.subtotal.toFixed(2)}</span>
            </div>
            <button className="btn btn-primary btn-lg" style={{ width: '100%', marginTop: 16 }}
              onClick={() => setCheckoutMode(true)}>
              Proceed to Checkout
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default CartPage;
