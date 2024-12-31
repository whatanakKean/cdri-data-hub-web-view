window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature, context) {
            const {
                classes,
                colorscale,
                style,
                colorProp
            } = context.hideout; // get props from hideout
            const value = feature.properties[colorProp]; // get value that determines the color

            if (value === null || value === undefined) {
                // If the value is None (null or undefined), set no color (transparent)
                style.fillColor = null; // or style.fillColor = 'transparent';
            } else {
                // Otherwise, check the classes and apply the colorscale
                for (let i = 0; i < classes.length; ++i) {
                    if (value > classes[i]) {
                        style.fillColor = colorscale[i]; // set the fill color according to the class
                    }
                }
            }
            return style;
        }
    }
});