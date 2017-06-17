
SearchView = {
    loader: ko.observable(false),
    dialogPropertySet: new PropertySet(),
    searchPropertySet: new PropertySet(),
    searchedItems: ko.observableArray([]),
    page: ko.observable(0),
    pages: ko.observable(0),
    operationModes: [
        {
            'text': 'Add',
            'sign': '+'
        },
        {
            'text': 'Subtract',
            'sign': '-'
        },
    ],

    selectedComponent: ko.observable(null),

    dialogError: ko.observable('Error Occured!'),

    alert: function(data) {
        console.log(data);
    },

    refreshPage: function() {
        this.load(this.page());
    },

    addComponent: function() {
        var data = ko.toJS(this.searchPropertySet);

        for (var index in data) {
            if (index.startsWith("property_")) {
                var val = data[index];
                this.dialogPropertySet[index](val);
            }
        }

        $("#addComponentModal").modal("show");
    },

    searchComponent: function() {
        var data = this.searchPropertySet.toJS();
        this.load(0);
    },

    load: function(page) {
        var _this = this;
        var v = _this.searchPropertySet.toJS();
        v['page'] = page;
        _this.callSearch(v, function(data) {
            if (data == null) {
                _this.alert("Error in executing search query.");
                return;
            }
            _this.page(parseInt(data.page));
            _this.pages(parseInt(data.pages));
            _this.searchedItems(data.data);
        });
    },

    callSearch: function(data, callback) {
        $.ajax({
            method: "POST",
            data: JSON.stringify(data),
            processData: false,
            contentType: "application/json",
            url: "/components/" + COMPONENT_TYPE_ID + "/search/",
            headers: {
                "X-CSRFTOKEN": CSRF_TOKEN
            }
        }).done(function(data) {
            callback(data);
        }).fail(function() {
            callback(null);
        });
    },

    next: function() {
        if (this.page() < (this.pages() - 1)) {
            this.load(this.page() + 1);
        }
    },

    previous: function() {
        if (this.page() > 0) {
            this.load(this.page() - 1);
        }
    },

    saveComponent: function() {
        var _this = this;
        _this.loader(true);
        _this.add(function(data) {
            _this.loader(false);
            if (data == null) {
                _this.alert("Error in saving component.");
                return;
            }
            _this.refreshPage();
        });
    },

    updateComponent: function() {

    },

    removeComponent: function(data) {
        var _this = SearchView;
        _this.selectedComponent(data);
        _this.updateMode('remove_component');
        $("#updateModal").modal("show");
    },

    add: function(callback) {
        var data = this.dialogPropertySet.toJS();
        $.ajax({
            method: "POST",
            data: JSON.stringify(data),
            processData: false,
            contentType: "application/json",
            url: "/components/" + COMPONENT_TYPE_ID + "/add/",
            headers: {
                "X-CSRFTOKEN": CSRF_TOKEN
            }
        }).done(function(data) {
            callback(data);
        }).fail(function() {
            callback(null);
        });
    },

    delete: function(id, callback) {
        $.ajax({
            method: "DELETE",
            url: "/inventory/" + id + "/",
            headers: {
                "X-CSRFTOKEN": CSRF_TOKEN
            }
        }).done(function(data) {
            callback(data);
        }).fail(function() {
            callback(null);
        });
    },

    updateMode: ko.observable(null),

    updateBox: function(data) {
        var _this = SearchView;
        _this.selectedComponent(data);
        _this.updateMode('change_box');
        $("#updateModal").modal("show");
    },

    addQuantity: function(data) {
        var _this = SearchView;
        _this.selectedComponent(data);
        _this.updateMode('add_quantity');
        $("#qInput").val(0);
        $("#updateModal").modal("show");
    },

    subtractQuantity: function(data) {
        var _this = SearchView;
        _this.selectedComponent(data);
        _this.updateMode('subtract_quantity');
        $("#qInput").val(0);
        $("#updateModal").modal("show");
    },

    updateSubmit: function() {
        var _this = this;
        if (_this.updateMode() == 'change_box') {
            var box = $("#boxInput").val();
            _this.loader(true);
            _this.saveBox(_this.selectedComponent().id, box, function(data) {
                _this.loader(false);
                if (data == null) {
                    _this.alert("Error in saving box.");
                    return;
                }
                _this.refreshPage();
            });

        } else if (_this.updateMode() == 'add_quantity') {
            var q = $("#qInput").val();
            var val = parseInt(q);
            _this.loader(true);
            _this.updateQuantity(_this.selectedComponent().id, val, function(data) {
                _this.loader(false);
                if (data == null) {
                    _this.alert("Error in changing quantity.");
                    return;
                }
                _this.refreshPage();
            });

        } else if (_this.updateMode() == 'subtract_quantity') {
            var q = $("#qInput").val();
            var val = parseInt(q);

            _this.loader(true);
            _this.updateQuantity(_this.selectedComponent().id, (-1) * val, function(data) {
                _this.loader(false);
                if (data == null) {
                    _this.alert("Error in changing quantity.");
                    return;
                }
                _this.refreshPage();
            });

        } else if (_this.updateMode() == 'remove_component') {
            _this.loader(true);
            _this.delete(_this.selectedComponent().id, function(data) {
                _this.loader(false);
                if (data == null) {
                    _this.alert("Error in deleting component.");
                    return;
                }
                _this.refreshPage();
            });
        }
    },

    saveBox: function(id, box, callback) {
        var _this = SearchView;
        $.ajax({
            method: "POST",
            data: {'box': box},
            url: "/inventory/" + id + "/update/box/",
            headers: {
                "X-CSRFTOKEN": CSRF_TOKEN
            }
        }).done(function(data) {
            callback(data);
        }).fail(function() {
            callback(null);
        });
    },

    updateQuantity: function(id, data, callback) {
        var _this = SearchView;
        $.ajax({
            method: "POST",
            data: {'diff': data},
            url: "/inventory/" + id + "/update/quantity/",
            headers: {
                "X-CSRFTOKEN": CSRF_TOKEN
            }
        }).done(function(data) {
            callback(data);
        }).fail(function() {
            callback(null);
        });
    },

    loadPropertyAutoComplete: function(data, t, e) {
        this.getPropertyValues(e.target, data);
    },

    getPropertyValues: function(target, property) {
        var _this = SearchView;
        var v = _this.searchPropertySet.toJS();
        v["property"] = property;
        $.ajax({
            method: "POST",
            data: JSON.stringify(v),
            processData: false,
            url: "/components/" + COMPONENT_TYPE_ID + "/property_values/",
            headers: {
                "X-CSRFTOKEN": CSRF_TOKEN
            }
        }).done(function(data) {
            $(target).autocomplete({
                source: data.property_values
            });
        })
    },

    init: function() {
        var _this = this;
        _this.nextDisable = ko.computed(function() {
            if (_this.pages() == 0) {
                return true;
            }
            return (_this.page() == (_this.pages() - 1));
        }, _this);

        _this.previousDisable = ko.computed(function() {
            return (_this.page() == 0);
        }, _this);

        _this.updateTitle = ko.computed(function() {
            if (_this.updateMode() == 'change_box') {
                return 'Change Box';
            } else if (_this.updateMode() == 'add_quantity') {
                return 'Add Quantity';
            } else if (_this.updateMode() == 'subtract_quantity') {
                return 'Subtract Quantity';
            } else if (_this.updateMode() == 'remove_component') {
                return 'Delete Component';
            }
            return '';
        }, _this);
    }
}

$(document).ready(function() {
    SearchView.init();

    ko.applyBindings(SearchView);

    SearchView.searchComponent();
});
