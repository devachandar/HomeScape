import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import client from "../api/client";
import { useAuth } from "../context/AuthContext.jsx";

const currency = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

export default function PropertyDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const [property, setProperty] = useState(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [sending, setSending] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    client
      .get(`/properties/${id}`)
      .then((res) => setProperty(res.data))
      .catch(() => setError("This listing could not be found."))
      .finally(() => setLoading(false));
  }, [id]);

  async function submitInquiry(e) {
    e.preventDefault();
    setSending(true);
    setError("");
    try {
      await client.post("/inquiries", { propertyId: id, message });
      setSent(true);
      setMessage("");
    } catch (err) {
      setError(err.response?.data?.error || "Could not send your message. Please sign in and try again.");
    } finally {
      setSending(false);
    }
  }

  if (loading) return <div className="container section">Loading listing…</div>;
  if (error && !property) return <div className="container section">{error}</div>;
  if (!property) return null;

  return (
    <section className="section container">
      <span className="eyebrow">
        {property.city}, {property.state} · {property.property_type}
      </span>
      <h1 style={{ fontSize: 34, marginTop: 8, marginBottom: 24 }}>{property.title}</h1>

      <div className="detail-hero">
        <div className="detail-gallery">
          {property.images?.length ? (
            <img src={property.images[0].url} alt={property.title} />
          ) : (
            <div
              className="property-thumb"
              style={{ aspectRatio: "16/10", borderRadius: 3 }}
            >
              NO IMAGES UPLOADED
            </div>
          )}
        </div>

        <div className="detail-panel ticked">
          <span className="eyebrow">Listing price</span>
          <h2 style={{ fontSize: 30, marginTop: 4 }}>{currency.format(property.price)}</h2>

          <div className="spec-list">
            <span>Bedrooms <strong style={{ color: "var(--ink)" }}>{property.bedrooms}</strong></span>
            <span>Bathrooms <strong style={{ color: "var(--ink)" }}>{property.bathrooms}</strong></span>
            <span>Sqft <strong style={{ color: "var(--ink)" }}>{property.square_feet || "—"}</strong></span>
            <span>Status <strong style={{ color: "var(--ink)" }}>{property.status}</strong></span>
          </div>

          {property.amenities?.length ? (
            <div style={{ marginBottom: 18 }}>
              {property.amenities.map((a) => (
                <span className="amenity-pill" key={a}>
                  {a.replace(/_/g, " ")}
                </span>
              ))}
            </div>
          ) : null}

          <h4 style={{ fontSize: 13, textTransform: "uppercase", color: "var(--slate)", marginBottom: 8 }}>
            Contact the seller
          </h4>

          {sent ? (
            <p style={{ color: "var(--pine)" }}>Your message was sent - the seller will follow up by email.</p>
          ) : user ? (
            <form onSubmit={submitInquiry}>
              {error && <div className="error-banner">{error}</div>}
              <textarea
                rows={4}
                required
                placeholder={`Hi, I'm interested in ${property.title}...`}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                style={{ width: "100%", padding: 10, border: "1px solid var(--line)", borderRadius: 3, marginBottom: 10, fontFamily: "inherit" }}
              />
              <button className="btn btn-brass btn-block" disabled={sending}>
                {sending ? "Sending…" : "Send message"}
              </button>
            </form>
          ) : (
            <p style={{ color: "var(--slate)", fontSize: 14 }}>
              <a href="/login" style={{ color: "var(--brass-dark)", fontWeight: 600 }}>
                Sign in
              </a>{" "}
              to contact this seller.
            </p>
          )}
        </div>
      </div>

      {property.description && (
        <div style={{ maxWidth: 720 }}>
          <h3 style={{ fontSize: 20, marginBottom: 10 }}>About this property</h3>
          <p style={{ color: "var(--slate)" }}>{property.description}</p>
        </div>
      )}
    </section>
  );
}
