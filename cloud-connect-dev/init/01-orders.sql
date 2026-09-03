-- Seeded once, on the container's first start.
CREATE TABLE public.orders (
  id          integer PRIMARY KEY,
  customer    text        NOT NULL,
  total_cents integer     NOT NULL,
  placed_at   timestamptz NOT NULL
);

INSERT INTO public.orders (id, customer, total_cents, placed_at) VALUES
  (1, 'acme',    12900, '2026-01-04T09:15:00Z'),
  (2, 'globex',   4550, '2026-01-04T11:02:00Z'),
  (3, 'initech', 31875, '2026-01-05T14:40:00Z'),
  (4, 'acme',      990, '2026-01-06T08:05:00Z'),
  (5, 'umbrella', 7625, '2026-01-06T16:22:00Z');
