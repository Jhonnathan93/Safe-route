import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import L from "leaflet";
import { CircleMarker, MapContainer, Marker, Polyline, TileLayer, Tooltip, useMapEvents } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerIconRetina from "leaflet/dist/images/marker-icon-2x.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";
import "./styles.css";

L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIconRetina,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

type Point = { lat: number; lng: number };
type SearchResult = { found: boolean; label: string; location: Point | null; nearest_node: (Point & { distance_m: number }) | null };
type Route = { coordinates: Point[]; distance_m: number; risk_score: number; origin_node: Point & { offset_m: number }; destination_node: Point & { offset_m: number } };
const API = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

async function geocode(query: string): Promise<SearchResult> {
  const response = await fetch(`${API}/routing/geocode/?q=${encodeURIComponent(query)}`);
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.message || "The location could not be searched.");
  return payload.data;
}

function PlaceInput({ title, onSelect, onRequestMapPoint }: { title: string; onSelect: (point: Point | undefined) => void; onRequestMapPoint: () => void }) {
  const [value, setValue] = useState("");
  const [result, setResult] = useState<SearchResult>();
  const [loading, setLoading] = useState(false);
  const search = async () => {
    if (!value.trim()) return;
    setLoading(true);
    try { const found = await geocode(value); setResult(found); onSelect(found.nearest_node || undefined); }
    catch (error) { setResult(undefined); alert(error instanceof Error ? error.message : "Search error"); }
    finally { setLoading(false); }
  };
  return <section className="place"><label>{title}</label><div className="search"><input value={value} onChange={e => setValue(e.target.value)} onKeyDown={e => e.key === "Enter" && search()} placeholder="E.g. Parque Lleras" /><button onClick={search} disabled={loading}>{loading ? "…" : "Search"}</button></div>
    {result && <p className={result.found ? "result" : "result warning"}>{result.found ? <>{result.label}<br /><small>Pedestrian node {result.nearest_node?.distance_m.toLocaleString("en-US")} m away</small></> : <>{result.label}<br /><button className="map-select" onClick={onRequestMapPoint}>Select point on map</button></>}</p>}</section>;
}

function MapPointSelector({ onSelect }: { onSelect: (point: Point) => void }) {
  useMapEvents({ click: event => onSelect({ lat: event.latlng.lat, lng: event.latlng.lng }) });
  return null;
}

function App() {
  const [origin, setOrigin] = useState<Point>();
  const [destination, setDestination] = useState<Point>();
  const [weight, setWeight] = useState(6);
  const [route, setRoute] = useState<Route>();
  const [error, setError] = useState("");
  const [mapSelection, setMapSelection] = useState<"origin" | "destination">();
  const selectMapPoint = (point: Point) => {
    if (mapSelection === "origin") setOrigin(point);
    if (mapSelection === "destination") setDestination(point);
    setMapSelection(undefined);
  };
  const calculate = async () => {
    if (!origin || !destination) { setError("Search for and select an origin and a destination."); return; }
    setError(""); setRoute(undefined);
    try {
      const response = await fetch(`${API}/routing/routes/`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ origin, destination, risk_weight: weight }) });
      const payload = await response.json(); if (!response.ok) throw new Error(payload.message); setRoute(payload.data);
    } catch (cause) { setError(cause instanceof Error ? cause.message : "The route could not be calculated."); }
  };
  return <main><aside><div className="brand"><span>◈</span><div><h1>Safe Route</h1><p>Walk with more information</p></div></div><p className="intro">Find a pedestrian route that balances distance and risk exposure.</p>
    <PlaceInput title="Starting point" onSelect={setOrigin} onRequestMapPoint={() => setMapSelection("origin")} /><PlaceInput title="Destination" onSelect={setDestination} onRequestMapPoint={() => setMapSelection("destination")} />
    {mapSelection && <p className="map-help">Click the map to set the {mapSelection === "origin" ? "starting point" : "destination"}.</p>}
    <section className="range"><div><label>Prioritize safety</label><strong>{weight}/10</strong></div><input type="range" min="0" max="10" value={weight} onChange={e => setWeight(Number(e.target.value))} /><div className="range-labels"><span>Shortest</span><span>Safest</span></div></section>
    <button className="primary" onClick={calculate}>Calculate safe route</button>{error && <p className="error">{error}</p>}
    {route && <section className="stats"><h2>Your route</h2><div><span>Distance</span><b>{route.distance_m >= 1000 ? `${(route.distance_m / 1000).toFixed(2)} km` : `${route.distance_m} m`}</b></div><div><span>Average risk</span><b>{route.risk_score}/100</b></div><small>Risk is weighted by the length of each segment.</small></section>}
  </aside><MapContainer center={[6.2442, -75.5812]} zoom={13} scrollWheelZoom className="map"><TileLayer attribution="© OpenStreetMap contributors" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
    {mapSelection && <MapPointSelector onSelect={selectMapPoint} />}
    {origin && <Marker position={origin}><Tooltip>Origen (nodo peatonal)</Tooltip></Marker>}{destination && <Marker position={destination}><Tooltip>Destino (nodo peatonal)</Tooltip></Marker>}
    {route && <><Polyline positions={route.coordinates} pathOptions={{ color: "#22c55e", weight: 6, opacity: .9 }} /><CircleMarker center={route.origin_node} radius={7} pathOptions={{ color: "#fff", fillColor: "#14532d", fillOpacity: 1 }} /><CircleMarker center={route.destination_node} radius={7} pathOptions={{ color: "#fff", fillColor: "#14532d", fillOpacity: 1 }} /></>}
  </MapContainer></main>;
}
createRoot(document.getElementById("root")!).render(<React.StrictMode><App /></React.StrictMode>);
