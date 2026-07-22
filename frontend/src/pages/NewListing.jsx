import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import client from "../api/client";

const initialForm = {
  title: "",
  description: "",
  propertyType: "house",
  price: "",
  bedrooms: 1,
  bathrooms: 1,
  squareFeet: "",
  addressLine1: "",
  city: "",
  state: "",
  postalCode: "",
  amenities: "",
};

export default function NewListing() {
  const [form, setForm] = useState(initialForm);
  const [files, setFiles] = useState([]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  function update(key, value) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitting(true);
    setError("");

    try {
      let images = [];
      if (files.length) {
        const data = new FormData();
        for (const file of files) data.append("images", file);
        const uploadRes = await client.post("/media/upload", data, {
          headers: { "Content-Type": "multipart/form-data" },
        });
        images = uploadRes.data.urls;
      }

      const payload = {
        ...form,
        price: Number(form.price),
        bedrooms: Number(form.bedrooms),
        bathrooms: Number(form.bathrooms),
        squareFeet: form.squareFeet ? Number(form.squareFeet) : undefined,
        amenities: form.amenities
          ? form.amenities.split(",").map((a) => a.trim().toLowerCase().replace(/\s+/g, "_")).filter(Boolean)
          : [],
        images,
      };

      const res = await client.post("/properties", payload);
      navigate(`/properties/${res.data.id}`);
    } catch (err) {
      setError(err.response?.data?.error || "Could not create this listing.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="section container" style={{ maxWidth: 720 }}>
      <span className="eyebrow">New listing</span>
      <h2 style={{ marginBottom: 24 }}>List a property</h2>

      {error && <div className="error-banner">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="field">
          <label htmlFor="title">Title</label>
          <input id="title" required value={form.title} onChange={(e) => update("title", e.target.value)} />
        </div>

        <div className="field">
          <label htmlFor="description">Description</label>
          <textarea
            id="description"
            rows={4}
            value={form.description}
            onChange={(e) => update("description", e.target.value)}
          />
        </div>

        <div className="field-row">
          <div className="field">
            <label htmlFor="propertyType">Property type</label>
            <select id="propertyType" value={form.propertyType} onChange={(e) => update("propertyType", e.target.value)}>
              <option value="house">House</option>
              <option value="apartment">Apartment</option>
              <option value="condo">Condo</option>
              <option value="townhouse">Townhouse</option>
              <option value="land">Land</option>
            </select>
          </div>
          <div className="field">
            <label htmlFor="price">Price (USD)</label>
            <input id="price" type="number" required value={form.price} onChange={(e) => update("price", e.target.value)} />
          </div>
        </div>

        <div className="field-row">
          <div className="field">
            <label htmlFor="bedrooms">Bedrooms</label>
            <input id="bedrooms" type="number" min="0" value={form.bedrooms} onChange={(e) => update("bedrooms", e.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="bathrooms">Bathrooms</label>
            <input id="bathrooms" type="number" min="0" step="0.5" value={form.bathrooms} onChange={(e) => update("bathrooms", e.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="squareFeet">Square feet</label>
            <input id="squareFeet" type="number" value={form.squareFeet} onChange={(e) => update("squareFeet", e.target.value)} />
          </div>
        </div>

        <div className="field">
          <label htmlFor="addressLine1">Address</label>
          <input id="addressLine1" required value={form.addressLine1} onChange={(e) => update("addressLine1", e.target.value)} />
        </div>

        <div className="field-row">
          <div className="field">
            <label htmlFor="city">City</label>
            <input id="city" required value={form.city} onChange={(e) => update("city", e.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="state">State</label>
            <input id="state" required value={form.state} onChange={(e) => update("state", e.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="postalCode">Postal code</label>
            <input id="postalCode" required value={form.postalCode} onChange={(e) => update("postalCode", e.target.value)} />
          </div>
        </div>

        <div className="field">
          <label htmlFor="amenities">Amenities (comma separated)</label>
          <input
            id="amenities"
            placeholder="garage, pool, central air"
            value={form.amenities}
            onChange={(e) => update("amenities", e.target.value)}
          />
        </div>

        <div className="field">
          <label htmlFor="images">Photos</label>
          <input id="images" type="file" accept="image/*" multiple onChange={(e) => setFiles([...e.target.files])} />
        </div>

        <button className="btn btn-brass btn-block" disabled={submitting}>
          {submitting ? "Publishing…" : "Publish listing"}
        </button>
      </form>
    </section>
  );
}
