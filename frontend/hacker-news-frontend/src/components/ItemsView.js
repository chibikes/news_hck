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
        };
      }

      componentDidMount() {
        this.getItems();
      }

      getItems = () => {
        $.ajax({
          url: `http://localhost:5000/items?page=${this.state.page}`, //TODO: update request URL
          type: 'GET',
          success: (result) => {
            this.setState({
              items: result.items,
              totalItems: result.total_items,
            });
            return;
          },
          error: (error) => {
            alert('Something went wrong. Couldn\'t load items');
            console.error('Error:', error);
            return;
          },
        });
      };

      render() {
        return(
            <div className='itemsView'>
                <div className='searchBar'>
                    <input type='text' placeholder='Search...'/>
                </div>
                <div>
                        {this.state.items.map((item) => (
                            <Item title={item.title} url={item.url} children={item.kids}/>
                        ))}
                </div>
            </div>
        );
      }
}

export default ItemsView;