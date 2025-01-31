django.jQuery(function ($) {
    $('.color-picker').spectrum({
        type: "component",
        preferredFormat: "hex",
        showInput: true,
        showInitial: true,
        showPalette: true,
        showSelectionPalette: true,
        maxSelectionSize: 10,
        palette: [
            ["#df2626", "#ff0000", "#ff4d4d", "#ff9999"],
            ["#00ff00", "#4dff4d", "#99ff99"],
            ["#0000ff", "#4d4dff", "#9999ff"]
        ]
    });
}); 