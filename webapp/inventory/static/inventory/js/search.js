
SearchView = {
    loader: ko.observable(false),
    dialogPropertySet: new PropertySet(),
    searchPropertySet: new PropertySet(),
    searchedItems: ko.observableArray([]),
    page: ko.observable(0),
    pages: ko.observable(0),
    modeSign: ko.observable('+'),
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

    boxValue: ko.observable(''),
    editBoxId: ko.observable(0),

    alert: function(data) {
        console.log(data);
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
        });
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

    updateBox: function(data) {
        var _this = SearchView;
        _this.boxValue(data.box);
        _this.editBoxId(data.id);
        $("#editBoxModal").modal("show");
    },

    saveBox: function() {
        var _this = SearchView;
        $.ajax({
            method: "POST",
            data: {'box': _this.boxValue()},
            url: "/inventory/" + _this.editBoxId() + "/update/box/",
            headers: {
                "X-CSRFTOKEN": CSRF_TOKEN
            }
        }).done(function(data) {
            _this.load(_this.page());
        });
    },

    updateQuantity: function(q, data) {
        var _this = SearchView;
        var val = parseInt(q);
        if (_this.modeSign() == '-') {
            val = (-1) *  val;
        }
        $.ajax({
            method: "POST",
            data: {'diff': val},
            url: "/inventory/" + data.id + "/update/",
            headers: {
                "X-CSRFTOKEN": CSRF_TOKEN
            }
        }).done(function(data) {
            _this.load(_this.page());
        });
    },

    loadPropertyAutoComplete: function(data, t, e) {
        this.getPropertyValues(e.target, data);
    },

    getPropertyValues: function(target, property) {
        $.getJSON("/components/" + COMPONENT_TYPE_ID + "/property_values/?property=" + property, function(data) {
            $(target).autocomplete({
                source: data.property_values
            });
        });
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
    }
}

$(document).ready(function() {
    SearchView.init();

    ko.applyBindings(SearchView);

    SearchView.searchComponent();
});
