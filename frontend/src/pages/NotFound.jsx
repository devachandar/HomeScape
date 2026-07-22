import React from "react";
import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="container section" style={{ textAlign: "center" }}>
      <span className="eyebrow">404</span>
      <h2 style={{ margin: "10px 0 18px" }}>This lot hasn't been surveyed.</h2>
      <Link to="/" className="btn btn-primary">
        Back home
      </Link>
    </div>
  );
}
