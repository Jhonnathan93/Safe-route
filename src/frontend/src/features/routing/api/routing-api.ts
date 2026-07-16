import { useMutation } from "@tanstack/react-query";
import { z } from "zod";

import { apiClient } from "@/lib/api-client";

export const pointSchema = z.object({ lat: z.number(), lng: z.number() });
const closestNodeSchema = pointSchema.extend({ distance_m: z.number() });
const snappedNodeSchema = pointSchema.extend({ offset_m: z.number() });

const geocodeResponseSchema = z.object({
  found: z.boolean(),
  label: z.string(),
  location: pointSchema.nullable(),
  nearest_node: closestNodeSchema.nullable(),
});

const routeResponseSchema = z.object({
  coordinates: z.array(pointSchema),
  distance_m: z.number(),
  risk_score: z.number(),
  origin_node: snappedNodeSchema,
  destination_node: snappedNodeSchema,
});

export type Point = z.infer<typeof pointSchema>;
export type GeocodeResponse = z.infer<typeof geocodeResponseSchema>;
export type RouteResponse = z.infer<typeof routeResponseSchema>;

export const useGeocode = () =>
  useMutation({
    mutationFn: (query: string) =>
      apiClient.get("/routing/geocode/", geocodeResponseSchema, { q: query }),
  });

export const useRouteCalculation = () =>
  useMutation({
    mutationFn: (payload: { origin: Point; destination: Point; risk_weight: number }) =>
      apiClient.post("/routing/routes/", payload, routeResponseSchema),
  });
