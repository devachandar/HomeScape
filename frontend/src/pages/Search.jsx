import React, { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import client from "../api/client";
import PropertyCard from "../components/PropertyCard.jsx";

const AMENITIES = ["garage", "pool", "pet_friendly", "in_unit_laundry", "central_air", "fireplace"];

export default function Search() {
  const [params, setParams] = useSearchParams();
  const [filters, setFilters] = useState({
    q: params.get("q") || "",
    city: "",
    propertyType: "",
    minPrice: "",
    maxPrice: "",
    bedrooms: "",
    sort: "relevance",
  });
  const [results, setResults] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function runSearch(activeFilters) {
    setLoading(true);
    setError("");
    try {
      const cleaned = Object.fromEntries(
        Object.entries(activeFilters).filter(([, v]) => v !== "" && v != null)
      );
      const res = await client.get("/search", { params: cleaned });
      setResults(res.data.results || []);
      setTotal(res.data.total || 0);
    } catch (err) {
      setError("Search is temporarily unavailable. Make sure search-service and Elasticsearch are running.");
      setResults([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    runSearch(filters);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function updateFilter(key, value) {
    setFilters((f) => ({ ...f, [key]: value }));
  }

  function handleSubmit(e) {
    e.preventDefault();
    setParams(filters.q ? { q: filters.q } : {});
    runSearch(filters);
  }

  return (
    <section className="section container">
      <div className="section-head">
        <div>
          <span className="eyebrow">Search</span>
          <h2>{total ? `${total} homes found` : "Browse homes"}</h2>
        </div>
      </div>

      <div className="search-layout">
        <form className="filters ticked" onSubmit={handleSubmit}>
          <div className="filter-group">
            <h4>Keyword</h4>
            <input
              className="field"
              style={{ width: "100%", padding: "10px 12px", border: "1px solid var(--line)", borderRadius: 3 }}
              placeholder="Neighborhood, street, keyword"
              value={filters.q}
              onChange={(e) => updateFilter("q", e.target.value)}
            />
          </div>

          <div className="filter-group">
            <h4>City</h4>
            <input
              style={{ width: "100%", padding: "10px 12px", border: "1px solid var(--line)", borderRadius: 3 }}
              placeholder="e.g. Buffalo"
              value={filters.city}
              onChange={(e) => updateFilter("city", e.target.value)}
            />
          </div>

          <div className="filter-group">
            <h4>Property type</h4>
            <select
              style={{ width: "100%", padding: "10px 12px", border: "1px solid var(--line)", borderRadius: 3 }}
              value={filters.propertyType}
              onChange={(e) => updateFilter("propertyType", e.target.value)}
            >
              <option value="">Any</option>
              <option value="house">House</option>
              <option value="apartment">Apartment</option>
              <option value="condo">Condo</option>
              <option value="townhouse">Townhouse</option>
              <option value="land">Land</option>
            </select>
          </div>

          <div className="filter-group">
            <h4>Price range</h4>
            <div className="filter-row">
              <input
                type="number"
                placeholder="Min"
                style={{ width: "50%", padding: "10px 12px", border: "1px solid var(--line)", borderRadius: 3 }}
                value={filters.minPrice}
                onChange={(e) => updateFilter("minPrice", e.target.value)}
              />
              <input
                type="number"
                placeholder="Max"
                style={{ width: "50%", padding: "10px 12px", border: "1px solid var(--line)", borderRadius: 3 }}
                value={filters.maxPrice}
                onChange={(e) => updateFilter("maxPrice", e.target.value)}
              />
            </div>
          </div>

          <div className="filter-group">
            <h4>Bedrooms (min)</h4>
            <select
              style={{ width: "100%", padding: "10px 12px", border: "1px solid var(--line)", borderRadius: 3 }}
              value={filters.bedrooms}
              onChange={(e) => updateFilter("bedrooms", e.target.value)}
            >
              <option value="">Any</option>
              {[1, 2, 3, 4, 5].map((n) => (
                <option key={n} value={n}>
                  {n}+
                </option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <h4>Sort</h4>
            <select
              style={{ width: "100%", padding: "10px 12px", border: "1px solid var(--line)", borderRadius: 3 }}
              value={filters.sort}
              onChange={(e) => updateFilter("sort", e.target.value)}
            >
              <option value="relevance">Relevance</option>
              <option value="newest">Newest</option>
              <option value="price_asc">Price: low to high</option>
              <option value="price_desc">Price: high to low</option>
            </select>
          </div>

          <button className="btn btn-primary btn-block" type="submit">
            Apply filters
          </button>
        </form>

        <div>
          {error && <div className="error-banner">{error}</div>}
          {loading ? (
            <p style={{ color: "var(--slate)" }}>Searching…</p>
          ) : results.length ? (
            <div className="property-grid">
              {results.map((p) => (
                <PropertyCard key={p.id} property={p} />
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <p>No matches yet. Try widening your filters, or list the first property.</p>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
