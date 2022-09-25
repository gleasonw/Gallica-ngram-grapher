import styled from "styled-components";

export const StyledOccurrenceTable = styled.table`
    border-collapse: collapse;
    table-layout: fixed;
    td{
        padding: 5px;
        border: 1px solid #ddd;
    }
    td:hover{
        overflow: visible;
        white-space: normal;
        height: auto;
    }
    tr:nth-child(even){
        background-color: #f2f2f2;
    }
    border: 3px solid #ddd;
`;