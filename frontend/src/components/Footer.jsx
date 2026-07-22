import React from "react";

export default function Footer() {
  return (
    <footer className="footer">
      <div className="container footer" style={{ borderTop: "none", margin: 0, padding: 0, width: "100%" }}>
        <span>© {new Date().getFullYear()} HomeScape - a portfolio system-design project.</span>
        <span>Auth · Property · Search · Inquiry · Media · Notification services</span>
      </div>
    </footer>
  );
}
