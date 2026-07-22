import React from "react";
import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar.jsx";
import Footer from "./components/Footer.jsx";
import RequireAuth from "./components/RequireAuth.jsx";

import Home from "./pages/Home.jsx";
import Search from "./pages/Search.jsx";
import PropertyDetail from "./pages/PropertyDetail.jsx";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import NewListing from "./pages/NewListing.jsx";
import NotFound from "./pages/NotFound.jsx";

export default function App() {
  return (
    <div>
      <Navbar />
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/search" element={<Search />} />
          <Route path="/properties/:id" element={<PropertyDetail />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/dashboard"
            element={
              <RequireAuth roles={["seller", "agent", "admin"]}>
                <Dashboard />
              </RequireAuth>
            }
          />
          <Route
            path="/dashboard/new"
            element={
              <RequireAuth roles={["seller", "agent", "admin"]}>
                <NewListing />
              </RequireAuth>
            }
          />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
      <div className="container">
        <Footer />
      </div>
    </div>
  );
}
