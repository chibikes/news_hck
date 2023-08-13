import React, { Component } from 'react';
import { useNavigate } from 'react-router-dom';

function Item(props) {
    const navigate = useNavigate();
    const handleButtonClick = () => {
        navigate(`/item/${props.id}`);
    };

    function timeAgo(unixTimestamp) {
        const currentTime = Date.now();
        const timestamp = new Date(unixTimestamp * 1000); // Convert to milliseconds

        const timeDifference = currentTime - timestamp;
        const minutesDifference = Math.floor(timeDifference / (60 * 1000));

        if (minutesDifference < 1) {
            return "Just now";
        } else if (minutesDifference === 1) {
            return "1 minute ago";
        } else if (minutesDifference < 60) {
            return `${minutesDifference} minutes ago`;
        } else {
            const hoursDifference = Math.floor(minutesDifference / 60);
            if (hoursDifference === 1) {
                return "1 hour ago";
            } else if (hoursDifference < 24) {
                return `${hoursDifference} hours ago`;
            } else {
                const daysDifference = Math.floor(hoursDifference / 24);
                if (daysDifference === 1) {
                    return "1 day ago";
                } else {
                    return `${daysDifference} days ago`;
                }
            }
        }
    }

    const decodeHtml = (encodedText) => {
        if (encodedText === null) return '';
        const parser = new DOMParser();
        const decodedDocument = parser.parseFromString(encodedText, 'text/html');
        return  decodedDocument.body.textContent;
    };

    const subtitle = {
        display: 'flex',
        alignItems: 'center',
        color: 'grey',
        fontSize: '12px',
        marginBottom: '5px',
    };

    const subtext = {
        display: 'flex',
        alignItems: 'center',
        color: 'black',
        fontSize: '12px',
    };
    const { title, url, children, time, id, text } = props;
    // getTime = () => {
    //     let unixTime = time;
    //     var date = new Date(unix_timestamp * 1000);
    // };

    return (
        <div className='ItemHolder'>
            <div className='ItemTitle' ><b><a href={url}>{title}</a></b></div>
            <div style={subtext} ><b>{decodeHtml(text)}</b></div>
            <div className='subTitle' style={subtitle}><div> {timeAgo(time)} </div> <div style={{ marginLeft: '10px' }}> <span onClick={handleButtonClick}>{children} comments</span></div></div>
        </div>
    );
}

export default Item;