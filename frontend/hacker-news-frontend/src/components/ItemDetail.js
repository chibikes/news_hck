import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import $ from 'jquery';

const ItemDetail = () => {
    const { itemid } = useParams();
    const [mainItem, setMainItem] = useState({});
    const [items, setItems] = useState([{}]);
    const [isLoading, setIsLoading] = useState(true); // Add a loading state

    useEffect(() => {
        getItems();
    }, []);

    const decodeHtml = (encodedText) => {
        const parser = new DOMParser();
        const decodedDocument = parser.parseFromString(encodedText, 'text/html');
        return decodedDocument.body.textContent;
    };

    const getItems = () => {
        setIsLoading(true); // Set loading to true before fetching
        $.ajax({
            url: `http://localhost:5000/items/${itemid}`,
            type: 'GET',
            success: (result) => {
                setMainItem(result.item);
                setItems(result.kids_items);
                setIsLoading(false); // Set loading to false after fetching
            },
            error: (error) => {
                setIsLoading(false); // Set loading to false in case of error
                alert('Something went wrong. Couldn\'t load items');
                console.error('Error:', error);
            },
        });
    };

    const commentStyle = {
        border: '1px solid #ccc',
        padding: '10px',
        margin: '10px 0',
    };

    const deleteStyle = {
        color: 'red',
        cursor: 'pointer',
    };

    return (
        <div style={{ fontFamily: 'Arial, sans-serif', margin: '20px' }}>
            {isLoading ? (
                <div>Loading...</div>
            ) : (
                <>
                    <div style={{ fontSize: '20px', fontWeight: 'bold' }}>{mainItem.title}</div>
                    {items.map((item, index) => (
                        <div key={index} style={commentStyle}>
                            <div style={{ fontSize: '16px', fontWeight: 'bold' }}>{item.title}</div>
                            <div>{decodeHtml(item.news_text)}</div>
                            <div style={deleteStyle}>1 comment delete</div>
                        </div>
                    ))}
                </>
            )}
        </div>
    );
}

export default ItemDetail;
