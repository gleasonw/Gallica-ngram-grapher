import React, { useEffect } from "react";
import { GraphTicket } from "./GraphTicket";
import { ProgressType } from "../models/dbStructs";
import { apiURL } from "./apiURL";
import { useQueries } from "@tanstack/react-query";

export const SearchProgress: React.FC<{
  batchTicket: GraphTicket[];
  onFetchComplete: () => void;
  onNoRecordsFound: () => void;
  onError: () => void;
}> = (props) => {
  async function fetchProgress(id: number) {
    const response = await fetch(`${apiURL}/poll/progress/${id}`);
    const data = (await response.json()) as ProgressType;
    return data;
  }
  const data = useQueries({
    queries: props.batchTicket.map((ticket) => ({
      queryKey: ["progress", ticket.id],
      queryFn: () => fetchProgress(ticket.id),
      //@ts-ignore
      refetchInterval: (data) => {
        if (
          data &&
          (data.state === "completed" ||
            data.state === "no_records" ||
            data.state === "error")
        ) {
          return false;
        } else {
          return 1000;
        }
      },
    })),
  });

  if (data && data.length === props.batchTicket.length) {
    if (data.every((ticket) => ticket?.data?.state === "completed")) {
      props.onFetchComplete();
    } else if (data.every((ticket) => ticket?.data?.state === "no_records")) {
      props.onNoRecordsFound();
    } else if (data.every((ticket) => ticket?.data?.state === "error")) {
      props.onError();
    }
  }

  return <></>;
};
