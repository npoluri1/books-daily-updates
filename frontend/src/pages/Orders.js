import React from 'react';
import { useApp } from '../context/AppContext';

const Orders = () => {
  const { orders, selectedCurrency, currencies, setPage } = useApp();
  const currencySymbol = currencies.find(c => c.code === selectedCurrency)?.symbol || '$';

  const statusColors = {
    confirmed: '#0071e3', processing: '#ff9f0a',
    shipped: '#30d158', delivered: '#30d158',
    cancelled: '#ff453a',
  };

  return (
    <div className="page page-3d">
      <div className="page-header">
        <h1 className="page-title text-3d-strong">My <span>Orders</span></h1>
        <p className="page-subtitle">Track your book orders and deliveries</p>
      </div>
      {orders.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📦</div>
          <h3>No Orders Yet</h3>
          <p>Your order history will appear here</p>
          <button className="btn btn-primary" style={{ marginTop: 16 }} onClick={() => setPage('library')}>
            Start Shopping
          </button>
        </div>
      ) : (
        <div className="orders-list">
          {orders.map(order => (
            <div key={order.id} className="card order-card card-3d-tilt shadow-3d">
              <div className="order-header">
                <div>
                  <h3>Order #{order.order_number}</h3>
                  <p className="order-date">
                    {new Date(order.created_at).toLocaleDateString('en-US', {
                      year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit'
                    })}
                  </p>
                </div>
                <div className="order-status-badge" style={{
                  background: statusColors[order.status] || '#6e6e73'
                }}>
                  {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                </div>
              </div>
              <div className="order-items">
                {order.items?.map(item => (
                  <div key={item.id} className="order-item">
                    {item.book?.images?.[0] && (
                      <img src={item.book.images[0].url} alt={item.book.title} className="order-item-cover" />
                    )}
                    <div className="order-item-info">
                      <strong>{item.book?.title || 'Book'}</strong>
                      <span>Qty: {item.quantity}</span>
                    </div>
                    <span className="order-item-price">
                      {currencySymbol}{item.unit_price.toFixed(2)}
                    </span>
                  </div>
                ))}
              </div>
              <div className="order-footer">
                <div className="order-totals">
                  <span>Subtotal: {currencySymbol}{order.subtotal.toFixed(2)}</span>
                  <span>Shipping: {currencySymbol}{order.shipping_cost.toFixed(2)}</span>
                  <span>Tax: {currencySymbol}{order.tax.toFixed(2)}</span>
                  <strong>Total: {currencySymbol}{order.total.toFixed(2)}</strong>
                </div>
                <div className="order-delivery">
                  {order.estimated_delivery && (
                    <div className="delivery-info">
                      <span className="badge badge-info">🚚 {order.estimated_delivery}</span>
                    </div>
                  )}
                  {order.payment_status === 'paid' && (
                    <span className="badge badge-success">✅ Paid</span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Orders;
