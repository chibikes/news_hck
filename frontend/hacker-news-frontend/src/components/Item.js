import React, { Component } from 'react';

class Item extends Component {

    render() {
        const subtitle = {
            color: 'grey',
            fontSize: '12px',
          };
        const {title, url, children, time} = this.props;
        getTime = () => {
            let unixTime = time;
            var date = new Date(unix_timestamp * 1000);
        };

        return(
            <div className='ItemHolder'>
                <div className='ItemTitle' ><b><a href={url}>{title}</a></b></div>
                <div className='subTitle' style={subtitle}> 2 minutes {children} comments</div>
            </div>
        );
    }
}

export default Item;