import { FormEvent, useState } from "react";

import { ApiError } from "@/lib/api-client";
import { Point, useGeocode } from "@/features/routing/api/routing-api";

type LocationSearchProps = {
  title: string;
  onLocationResolved: (point: Point | undefined) => void;
  onRequestMapPoint: () => void;
};

export function LocationSearch({ title, onLocationResolved, onRequestMapPoint }: LocationSearchProps) {
  const [query, setQuery] = useState("");
  const geocode = useGeocode();

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!query.trim()) return;
    geocode.mutate(query, {
      onSuccess: result => onLocationResolved(result.nearest_node ?? undefined),
    });
  };

  const errorMessage = geocode.error instanceof ApiError ? geocode.error.message : "Search failed.";

  return (
    <section className="place">
      <label>{title}</label>
      <form className="search" onSubmit={handleSubmit}>
        <input value={query} onChange={event => setQuery(event.target.value)} placeholder="E.g. Parque Lleras" />
        <button disabled={geocode.isPending} type="submit">
          {geocode.isPending ? "Loading…" : "Search"}
        </button>
      </form>
      {geocode.isError && <p className="error">{errorMessage}</p>}
      {geocode.data && (
        <p className={geocode.data.found ? "result" : "result warning"}>
          {geocode.data.label}
          {geocode.data.nearest_node ? (
            <small>Pedestrian node {geocode.data.nearest_node.distance_m.toLocaleString("en-US")} m away</small>
          ) : (
            <button className="map-select" onClick={onRequestMapPoint} type="button">
              Select point on map
            </button>
          )}
        </p>
      )}
    </section>
  );
}
