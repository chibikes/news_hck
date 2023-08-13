import React, { Component } from 'react';
import Item from './Item';
import $ from 'jquery';

class ItemsView extends Component {
    constructor() {
        super();
        this.state = {
            items: [],
            page: 1,
            totalItems: 0,
            type: 'story',
            searchText: ''
        };
    }

    componentDidMount() {
        this.getItems();
    }

    handleSelectedItem = (event) => {
        this.setState({ type: event.target.value, page: 1 }, () => {
            this.getItems();
        });
    };

    submitSearch = (event) => {
        alert('change');
        const { searchText } = this.state;
        alert(searchText);
        $.ajax({
            url: `http://localhost:5000/search/items`,
            type: 'POST',
            dataType: 'json',
            contentType: 'application/json',
            data: JSON.stringify({ searchTerm: searchText }),
            success: (result) => {
                this.setState({
                    items: result.items,
                    totalItems: result.total_items,
                });
                return;
            },
            error: (error) => {
                console.log(`Error: ${error.text}`);
                alert('Unable to get items. Please try your request again');
                return;
            },
        });
    };

    getItems = () => {
        $.ajax({
            url: `http://localhost:5000/items?page=${this.state.page}&type=${this.state.type}`,
            type: 'GET',
            success: (result) => {
                this.setState({
                    items: result.items,
                    totalItems: result.total_items,
                });
            },
            error: (error) => {
                alert('Something went wrong. Couldn\'t load items');
                console.error('Error:', error);
            },
        });
    };

    updatePage = (number) => {
        this.setState({ page: number }, () => {
            this.getItems();
        });
    };

    createPagination() {
        let pageNumbers = [];
        let maxPage = Math.ceil(this.state.totalItems / 10);
        for (let i = 1; i <= maxPage; i++) {
            pageNumbers.push(i);
        }
        return pageNumbers;
    }

    render() {
        const styles = {
            itemsView: {
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                padding: '0 20px',
                height: '100vh',
                // textAlign: 'center'
            },
            searchBar: {
                marginBottom: '10px',
            },
            searchInput: {
                width: '200px',
                // padding: '5px',
            },
            select: {
                marginBottom: '10px',
            },
            footer: {
                display: 'flex',
            },
            pageBox: {
                width: '14px',
                height: '14px',
                border: '1px solid black',
                padding: '5px',
                margin: '10px',
                cursor: 'pointer',
            },
            pageText: {
                color: 'grey',
                fontSize: '12px',
            },
            searchButton: {
                marginLeft: '10px',
                cursor: 'pointer',
            },
        };

        return (
            <div style={styles.itemsView}>
                <form>
                    <div style={styles.searchBar}>
                        <input type='text' placeholder='search news by title or text' onChange={(event) => this.setState({ searchText: event.target.value })} style={styles.searchInput}/>
                        <button style={styles.searchButton} onClick={(event) => {
                            event.preventDefault(); // Prevent form submission
                            this.submitSearch();
                        }}>
                            <i className="fa fa-search" aria-hidden="true"></i>
                        </button>
                    </div>
                    <select style={styles.select} onChange={this.handleSelectedItem}>
                        <option>story</option>
                        <option>comment</option>
                        <option>poll</option>
                        <option>job</option>
                        <option>pollopt</option>
                    </select>
                </form>
                <div>
                    {this.state.items.map((item) => (
                        <Item
                            key={item.item_id}
                            title={item.title}
                            url={item.url}
                            children={item.kids_count}
                            id={item.item_id}
                            time={item.time}
                            text={item.text}
                        />
                    ))}
                </div>
                <button>Add News</button>
                <div style={styles.footer}>
                    {this.createPagination().map((i) => (
                        <div
                            key={i}
                            style={styles.pageBox}
                            onClick={() => {
                                this.updatePage(i);
                            }}
                        >
                            <div style={styles.pageText}>{i}</div>
                        </div>
                    ))}
                </div>
            </div>
        );
    }
}

export default ItemsView;