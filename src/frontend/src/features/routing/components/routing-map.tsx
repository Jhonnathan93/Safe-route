import L from "leaflet";
import { CircleMarker, MapContainer, Marker, Polyline, TileLayer, Tooltip, useMapEvents } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerIconRetina from "leaflet/dist/images/marker-icon-2x.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

import { Point, RouteResponse } from "@/features/routing/api/routing-api";

L.Icon.Default.mergeOptions({ iconRetinaUrl: markerIconRetina, iconUrl: markerIcon, shadowUrl: markerShadow });

type RoutingMapProps = {
  origin?: Point;
  destination?: Point;
  mapSelection?: "origin" | "destination";
  onMapPointSelected: (point: Point) => void;
  route?: RouteResponse;
};

function MapPointSelector({ onSelect }: { onSelect: (point: Point) => void }) {
  useMapEvents({ click: event => onSelect({ lat: event.latlng.lat, lng: event.latlng.lng }) });
  return null;
}

export function RoutingMap({ origin, destination, mapSelection, onMapPointSelected, route }: RoutingMapProps) {
  return (
    <MapContainer center={[6.2442, -75.5812]} className="map" scrollWheelZoom zoom={13}>
      <TileLayer attribution="© OpenStreetMap contributors" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {mapSelection && <MapPointSelector onSelect={onMapPointSelected} />}
      {origin && <Marker position={origin}><Tooltip>Origin</Tooltip></Marker>}
      {destination && <Marker position={destination}><Tooltip>Destination</Tooltip></Marker>}
      {route && (
        <>
          <Polyline pathOptions={{ color: "#22c55e", weight: 6, opacity: 0.9 }} positions={route.coordinates} />
          <CircleMarker center={route.origin_node} pathOptions={{ color: "#fff", fillColor: "#14532d", fillOpacity: 1 }} radius={7} />
          <CircleMarker center={route.destination_node} pathOptions={{ color: "#fff", fillColor: "#14532d", fillOpacity: 1 }} radius={7} />
        </>
      )}
    </MapContainer>
  );
}
