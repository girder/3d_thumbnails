import _ from 'underscore';
import { getApiRoot } from 'girder/rest';
import View from 'girder/views/View';
import PaginateWidget from 'girder/views/widgets/PaginateWidget';

import ViewerWidget from '../viewer/ViewerWidget';
import template from './folderListView.pug';
import './folderListView.styl';

const FolderListView = View.extend({
    initialize: function (settings) {
        this.folder = settings.folder;
        this.items = settings.items;
        this._viewers = [];
        this._pager = new PaginateWidget({
            parentView: this,
            collection: this.items
        });

        this.listenTo(this.items, 'g:changed', () => {
            this.render();
        });

        // TODO something in scheme to indicate http vs https
        this._pvDesktopUri = `paraview+girder://${window.location.host}/${getApiRoot()}`;
    },

    render: function () {
        this.$el.html(template({
            folder: this.folder,
            items: this.items,
            pvDesktopUri: this._pvDesktopUri
        }));

        this._cleanupViewers();
        this._viewers = _.map(this.$('.g-viewer-widget-wrapper'), (el) => {
            return new ViewerWidget({
                el,
                model: this.items.get($(el).attr('item-cid')),
                parentView: this
            }).render();
        });

        this._pager.setElement(this.$('.g-paginate-container')).render();
    },

    _cleanupViewers: function () {
        _.each(this._viewers, (viewer) => {
            viewer.destroy();
        });
    }
});

export default FolderListView;
