import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import client from "../api/client";
import PropertyCard from "../components/PropertyCard.jsx";

export default function Home() {
  const [query, setQuery] = useState("");
  const [featured, setFeatured] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    client
      .get("/properties", { params: { limit: 6 } })
      .then((res) => setFeatured(res.data.results || []))
      .catch(() => setFeatured([]))
      .finally(() => setLoading(false));
  }, []);

  function handleSearch(e) {
    e.preventDefault();
    navigate(`/search${query ? `?q=${encodeURIComponent(query)}` : ""}`);
  }

  return (
    <>
      <section className="hero">
        <div className="hero-grid" aria-hidden="true" />
        <div className="container hero-content">
          <span className="eyebrow" style={{ color: "#c9a15b" }}>
            HomeScape / property survey &amp; listing platform
          </span>
          <h1 style={{ marginTop: 10 }}>
            Every home, <span className="accent">plotted, priced,</span> and ready to view.
          </h1>
          <p className="lede">
            Search active listings across the country, message sellers directly, and track
            every inquiry in one place - built as a microservices reference architecture.
          </p>

          <form className="search-bar" onSubmit={handleSearch}>
            <input
              placeholder="Try “3 bedroom house in Buffalo”"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <button className="btn btn-brass" type="submit">
              Search
            </button>
          </form>

          <div className="hero-stats">
            <div>
              <strong>10M+</strong>
              <span>Users supported</span>
            </div>
            <div>
              <strong>100M+</strong>
              <span>Properties indexed</span>
            </div>
            <div>
              <strong>&lt;200ms</strong>
              <span>Search latency target</span>
            </div>
          </div>
        </div>
      </section>

      <section className="section container">
        <div className="section-head">
          <div>
            <span className="eyebrow">Fresh on the market</span>
            <h2>Featured listings</h2>
          </div>
          <a href="/search" className="btn btn-ghost">
            Browse all
          </a>
        </div>

        {loading ? (
          <p style={{ color: "var(--slate)" }}>Loading listings…</p>
        ) : featured.length ? (
          <div className="property-grid">
            {featured.map((p) => (
              <PropertyCard key={p.id} property={p} />
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <p>
              No listings yet - once the property service is seeded, they'll show up here.
            </p>
          </div>
        )}
      </section>
    </>
  );
}
