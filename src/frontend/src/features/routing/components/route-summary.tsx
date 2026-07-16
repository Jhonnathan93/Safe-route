import { RouteResponse } from "@/features/routing/api/routing-api";

export function RouteSummary({ route }: { route: RouteResponse }) {
  const distance = route.distance_m >= 1000 ? `${(route.distance_m / 1000).toFixed(2)} km` : `${route.distance_m} m`;
  return (
    <section className="stats">
      <h2>Your route</h2>
      <div><span>Distance</span><b>{distance}</b></div>
      <div><span>Average risk</span><b>{route.risk_score}/100</b></div>
      <small>Risk is weighted by the length of each segment.</small>
    </section>
  );
}
