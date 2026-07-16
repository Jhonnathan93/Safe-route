import { lazy, Suspense, useState } from "react";

import { ErrorBoundary } from "@/app/error-boundary";
import { ApiError } from "@/lib/api-client";
import { Point, useRouteCalculation } from "@/features/routing/api/routing-api";
import { LocationSearch } from "@/features/routing/components/location-search";
import { RouteSummary } from "@/features/routing/components/route-summary";

const RoutingMap = lazy(() => import("@/features/routing/components/routing-map").then(module => ({ default: module.RoutingMap })));

export function RoutingPage() {
  const [origin, setOrigin] = useState<Point>();
  const [destination, setDestination] = useState<Point>();
  const [riskWeight, setRiskWeight] = useState(6);
  const [mapSelection, setMapSelection] = useState<"origin" | "destination">();
  const routeCalculation = useRouteCalculation();

  const selectMapPoint = (point: Point) => {
    if (mapSelection === "origin") setOrigin(point);
    if (mapSelection === "destination") setDestination(point);
    setMapSelection(undefined);
  };

  const calculateRoute = () => {
    if (!origin || !destination) return;
    routeCalculation.mutate({ origin, destination, risk_weight: riskWeight });
  };

  const errorMessage = routeCalculation.error instanceof ApiError ? routeCalculation.error.message : "The route could not be calculated.";

  return (
    <main>
      <aside>
        <div className="brand"><span>◈</span><div><h1>Safe Route</h1><p>Walk with more information</p></div></div>
        <p className="intro">Find a pedestrian route that balances distance and risk exposure.</p>
        <LocationSearch onLocationResolved={setOrigin} onRequestMapPoint={() => setMapSelection("origin")} title="Starting point" />
        <LocationSearch onLocationResolved={setDestination} onRequestMapPoint={() => setMapSelection("destination")} title="Destination" />
        {mapSelection && <p className="map-help">Click the map to set the {mapSelection === "origin" ? "starting point" : "destination"}.</p>}
        <section className="range"><div><label>Prioritize safety</label><strong>{riskWeight}/10</strong></div><input max="10" min="0" onChange={event => setRiskWeight(Number(event.target.value))} type="range" value={riskWeight} /><div className="range-labels"><span>Shortest</span><span>Safest</span></div></section>
        <button className="primary" disabled={routeCalculation.isPending || !origin || !destination} onClick={calculateRoute}>{routeCalculation.isPending ? "Calculating…" : "Calculate safe route"}</button>
        {!origin || !destination ? <p className="map-help">Select both points to calculate a route.</p> : null}
        {routeCalculation.isError && <p className="error">{errorMessage}</p>}
        {routeCalculation.data && <RouteSummary route={routeCalculation.data} />}
      </aside>
      <ErrorBoundary fallback={<div className="map map-loading">The map could not be loaded.</div>}>
        <Suspense fallback={<div className="map map-loading">Loading map…</div>}>
          <RoutingMap destination={destination} mapSelection={mapSelection} onMapPointSelected={selectMapPoint} origin={origin} route={routeCalculation.data} />
        </Suspense>
      </ErrorBoundary>
    </main>
  );
}
