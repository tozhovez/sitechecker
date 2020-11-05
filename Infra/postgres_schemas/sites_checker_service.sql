

CREATE SEQUENCE reports_request_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 1;

CREATE TABLE "public"."reports" (
    "request_id" integer DEFAULT nextval('reports_request_id_seq') NOT NULL,
    "request" character varying(250) NOT NULL,
    "last_updated" timestamp NOT NULL,
    "risk" character varying(10) DEFAULT 'risk' NOT NULL,
    "total_voting" jsonb DEFAULT '"{}"' NOT NULL,
    "classification" jsonb DEFAULT '"{}"' NOT NULL,
    "link" character varying(500),
    CONSTRAINT "reports_request" UNIQUE ("request"),
    CONSTRAINT "reports_request_id" PRIMARY KEY ("request_id")
) WITH (oids = false);

COMMENT ON COLUMN "public"."reports"."risk" IS 'risk, safe';


DROP TABLE IF EXISTS "requests";
CREATE TABLE "public"."requests" (
    "request_id" integer NOT NULL,
    "date" date NOT NULL,
    "number_of_requests" integer DEFAULT '0' NOT NULL,
    CONSTRAINT "requests_request_id_date" UNIQUE ("request_id", "date"),
    CONSTRAINT "requests_request_id_fkey" FOREIGN KEY (request_id) REFERENCES reports(request_id) ON UPDATE CASCADE NOT DEFERRABLE
) WITH (oids = false);


DROP TABLE IF EXISTS "tasks";
CREATE TABLE "public"."tasks" (
    "location_request" character varying(500) NOT NULL,
    "location_report" character varying(500) NOT NULL,
    "time_created_task" timestamp NOT NULL
) WITH (oids = false);
