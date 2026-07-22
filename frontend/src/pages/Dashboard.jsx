import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import client from "../api/client";

const currency = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

export default function Dashboard() {
  const [listings, setListings] = useState([]);
  const [inquiries, setInquiries] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([client.get("/properties/seller/mine"), client.get("/inquiries/received")])
      .then(([listingsRes, inquiriesRes]) => {
        setListings(listingsRes.data || []);
        setInquiries(inquiriesRes.data || []);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  async function removeListing(id) {
    if (!confirm("Remove this listing? This can't be undone.")) return;
    await client.delete(`/properties/${id}`);
    setListings((list) => list.filter((l) => l.id !== id));
  }

  return (
    <section className="section container">
      <div className="dash-header">
        <div>
          <span className="eyebrow">Seller dashboard</span>
          <h2>Your listings</h2>
        </div>
        <Link to="/dashboard/new" className="btn btn-brass">
          + New listing
        </Link>
      </div>

      {loading ? (
        <p style={{ color: "var(--slate)" }}>Loading…</p>
      ) : listings.length ? (
        <table className="table">
          <thead>
            <tr>
              <th>Property</th>
              <th>City</th>
              <th>Price</th>
              <th>Status</th>
              <th>Listed</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {listings.map((p) => (
              <tr key={p.id}>
                <td>
                  <Link to={`/properties/${p.id}`}>{p.title}</Link>
                </td>
                <td>{p.city}, {p.state}</td>
                <td>{currency.format(p.price)}</td>
                <td>
                  <span className={`status-pill status-${p.status}`}>{p.status}</span>
                </td>
                <td>{new Date(p.created_at).toLocaleDateString()}</td>
                <td>
                  <button className="btn btn-ghost" onClick={() => removeListing(p.id)}>
                    Remove
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <div className="empty-state">
          <p>You haven't listed a property yet.</p>
          <Link to="/dashboard/new" className="btn btn-primary" style={{ marginTop: 12 }}>
            List your first property
          </Link>
        </div>
      )}

      <div style={{ marginTop: 48 }}>
        <h3 style={{ fontSize: 20, marginBottom: 14 }}>Inbox</h3>
        {inquiries.length ? (
          <table className="table">
            <thead>
              <tr>
                <th>Message</th>
                <th>Type</th>
                <th>Status</th>
                <th>Received</th>
              </tr>
            </thead>
            <tbody>
              {inquiries.map((i) => (
                <tr key={i.id}>
                  <td>{i.message}</td>
                  <td>{i.type}</td>
                  <td>
                    <span className="status-pill status-active">{i.status}</span>
                  </td>
                  <td>{new Date(i.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p style={{ color: "var(--slate)" }}>No inquiries yet.</p>
        )}
      </div>
    </section>
  );
}
