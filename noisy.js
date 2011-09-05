/*jQuery-Noise Plugin Originally Written By the Forrst Users @dhotson & @ajcates.
===============================================================================

Authors:
--------

@dhotson
:	"Dennis Hotson"
	- Email
	:	dennis.hotson@gmail.com
	- Forrst
	:	http://forrst.com/people/dhotson
	- Twitter
	:	@dennishotson
	- Tumblr
	:	http://dhotson.tumblr.com

@ajcates
:	"A.J. Cates"
	- Email
	:	aj@ajcates.com
	- Forrst
	:	http://forrst.com/people/ajcates
	- Twitter
	:	@dennishotson
	- Tumblr
	:	http://ajcates.tumblr.com


License:
--------

Copyright (c) 2010 @dhotson & @ajcates

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.*/

(function($) {
	$.fn.extend({
		noisy : function(params) {
			return $.extend({
				noiseMaker : $.extend({
					opacity : .05,
					width : 20,
					amount : 70,
					color: function() {
						return this.caller.css("background-color");
					},
					bringNoise : function() {
						var x, y,
			            	canvas = $("<canvas>", {width: this.width, height:this.width })[0],
			            	ctx = canvas.getContext("2d"),
			            	colorArr = (typeof(this.color) == "function" ?  this.color() : this.color).split(","),
			            	r = colorArr[0].replace("rgb(","").trim(), g = colorArr[1].trim(), b = colorArr[2].replace(")","").trim();
						for (x=0; x<canvas.width; x += 1) {
							for (y=0; y<canvas.height; y += 1) {
								ctx.fillStyle = "rgba(" + [
									Math.floor(Math.random() * r + this.amount), Math.floor(Math.random() * g + this.amount), Math.floor(Math.random() * b + this.amount),
									this.opacity
								].join(",") + ")";
								ctx.fillRect(x, y, 1, 1);
							}
			            }
			            return canvas.toDataURL("image/png");
					},
					go : function(caller) {
						this.caller = caller;
			            var noise = this.bringNoise();
			            return caller.css("background-image", function(i, val) {
			            	return "url("+noise+")" + ", " + val;
			            });
					}
				}, params)
			}).noiseMaker.go(this);
		}
	});
})(jQuery);