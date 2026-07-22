import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <header className="navbar">
      <div className="container navbar-inner">
        <Link to="/" className="brand">
          <span className="brand-mark" aria-hidden="true" />
          HomeScape
        </Link>

        <nav className="nav-links">
          <Link to="/search">Browse homes</Link>
          {user?.role === "seller" || user?.role === "agent" || user?.role === "admin" ? (
            <Link to="/dashboard">Seller dashboard</Link>
          ) : null}
        </nav>

        <div className="nav-actions">
          {user ? (
            <>
              <span className="nav-user">Hi, {user.fullName?.split(" ")[0] || user.full_name}</span>
              <button
                className="btn btn-ghost"
                onClick={() => {
                  logout();
                  navigate("/");
                }}
              >
                Sign out
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn-ghost">
                Sign in
              </Link>
              <Link to="/register" className="btn btn-primary">
                List a property
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
