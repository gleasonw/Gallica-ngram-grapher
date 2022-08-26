import React, {useState, useEffect} from "react";
import Button from "@mui/material/Button";
import {useContext} from "react";
import {GraphSettingsContext} from "./GraphSettingsContext";

export function TicketPaperOccurrenceStats(props) {
    const [topPapers, setTopPapers] = useState([]);
    const settings = useContext(GraphSettingsContext);
    const ticketSettings = props.grouped ? settings.group : settings[props.ticketID];
    useEffect(() => {
        let updatedPapers = [];
        fetch(
            "/api/topPapers?id="+props.ticketID+
            "&continuous="+ticketSettings.continuous+
            "&dateRange="+props.dateRange)
            .then(res => res.json())
            .then(result => {
                updatedPapers = result["topPapers"]
                setTopPapers(updatedPapers)
            })
    }, [props.dateRange, props.ticketID, ticketSettings.continuous, ticketSettings.dateRange])

    return (
        <div className='ticketStats'>
            <table className='topPaperTable'>
                <tbody>
                    <tr>
                        <th>Paper</th>
                        <th>Total Occurrences</th>
                    </tr>
                    {topPapers.map(paperCount => (
                        <tr key={paperCount[0]}>
                            <td>{paperCount[0]}</td>
                            <td>{paperCount[1]}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
            <Button variant='text'>
                Download full result CSV
            </Button>
        </div>
    )
}

export default TicketPaperOccurrenceStats;