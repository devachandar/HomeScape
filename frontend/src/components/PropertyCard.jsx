import React from "react";
import { Link } from "react-router-dom";

const currency = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

export default function PropertyCard({ property }) {
  const image = property.images?.[0]?.url;
  return (
    <Link to={`/properties/${property.id}`} className="property-card ticked">
      <div className="property-thumb">
        {image ? <img src={image} alt={property.title} /> : <span>NO IMAGE ON FILE</span>}
        <span className="property-price-tag">{currency.format(property.price)}</span>
      </div>
      <div className="property-body">
        <h3>{property.title}</h3>
        <p className="property-loc">
          {property.city}, {property.state}
        </p>
        <div className="property-meta">
          <span>{property.bedrooms} bd</span>
          <span>{property.bathrooms} ba</span>
          {property.square_feet ? <span>{property.square_feet} sqft</span> : null}
        </div>
      </div>
    </Link>
  );
}
