/* Execute inside After Effects, not Node. Does not modify the original comp.
   Set $.global.HOOK_ZOOM_OPTIONS={start:0,end:1.5,travel:200} before execution.
   Defaults to video time zero through 1.5 seconds, never the work area/playhead.
*/
(function () {
    var original=app.project.activeItem;
    if (!(original instanceof CompItem)) throw new Error('Select the finished scene composition first');
    var opts=$.global.HOOK_ZOOM_OPTIONS || {};
    var start=opts.start===undefined ? 0 : Number(opts.start);
    var end=opts.end===undefined ? 1.5 : Number(opts.end);
    var travel=(opts.travel===undefined ? 200 : Number(opts.travel))*original.width/1080;
    if(!isFinite(start)||!isFinite(end)||!isFinite(travel)||start<0||end<=start||end>original.duration+1e-7||travel<0)
        throw new Error('Invalid requested interval or camera travel');
    var distance=1500*original.width/1080;
    if(travel>=distance)throw new Error('Camera travel reaches or crosses the scene plane');
    var hasPlan=opts.keyPlan!==undefined;
    if(hasPlan){
        if(!(opts.keyPlan instanceof Array) || opts.keyPlan.length===0)
            throw new Error('Merged keyPlan must be a nonempty array');
        for(var p=0;p<opts.keyPlan.length;p++){
            var candidate=opts.keyPlan[p];
            if(!candidate || typeof candidate.time!=='number' || typeof candidate.z!=='number' ||
               !isFinite(candidate.time)||!isFinite(candidate.z)||candidate.time<0||
               candidate.time>original.duration||candidate.z>=distance ||
               (p>0 && candidate.time<=opts.keyPlan[p-1].time))
                throw new Error('Invalid or unordered merged keyPlan');
        }
    }
    app.beginUndoGroup('Hook Zoom Out 75/75');
    try {
        var work=original.duplicate();
        work.name=original.name+' — Hook Zoom Out';
        var oldControl=null,oldCamera=null;
        for(var r=1;r<=work.numLayers;r++){
            var existing=work.layer(r);
            if(existing.name==='Body Zoom Control' || existing.name==='Hook Zoom Out Control'){
                if(oldControl!==null)throw new Error('Multiple scene zoom controls found; merge rigs explicitly');
                if(!(existing instanceof AVLayer) || !existing.nullLayer)
                    throw new Error('Body Zoom Control name belongs to a non-null layer');
                oldControl=existing;
            }
            if((existing.name==='Body Zoom Camera' || existing.name==='Hook Zoom Out Camera') && existing instanceof CameraLayer){
                if(oldCamera!==null)throw new Error('Multiple scene zoom cameras found; merge rigs explicitly');
                oldCamera=existing;
            }
        }
        var reuse=oldControl!==null && oldCamera!==null;
        if(reuse){
            for(var extra=1;extra<=work.numLayers;extra++){
                var content=work.layer(extra);
                if(content===oldControl || content===oldCamera)continue;
                if(content instanceof CameraLayer || content instanceof LightLayer ||
                   (content instanceof AVLayer && content.adjustmentLayer))
                    throw new Error('Reused rig has new camera/light/adjustment content; preserve it in a scene group before updating the rig');
                if(content instanceof AVLayer && content.threeDLayer){
                    var cp=content.property('ADBE Transform Group').property('ADBE Position');
                    if(Math.abs(cp.value[2])>1e-7)
                        throw new Error('Reused rig contains depth-offset content; integrate the scene plane explicitly');
                }
            }
        }
        var complex=false;
        for(var i=1;i<=work.numLayers;i++){
            var test=work.layer(i);
            if(test instanceof CameraLayer || test instanceof LightLayer ||
               (test instanceof AVLayer && (test.threeDLayer || test.adjustmentLayer)))complex=true;
        }
        var comp=work;
        if(complex && !reuse){
            // Preserve existing camera/depth/adjustment behavior by treating the
            // already composed scene as one 3D plane under the new shared camera.
            comp=app.project.items.addComp(work.name+' Master',work.width,work.height,
                work.pixelAspect,work.duration,work.frameRate);
            var scene=comp.layers.add(work);
            scene.name='Hook Zoom Out Scene — all content';
            scene.threeDLayer=true;scene.motionBlur=true;scene.collapseTransformation=false;
            scene.property('ADBE Transform Group').property('ADBE Position').setValue([comp.width/2,comp.height/2,0]);
        } else {
            // For ordinary 2D editing stacks, enable 3D on every renderable layer.
            // Keep existing layer order, local transforms, sources and parent trees.
            for(var j=1;j<=comp.numLayers;j++){
                var layer=comp.layer(j);
                if(layer instanceof AVLayer && layer.hasVideo){
                    var locked=layer.locked;layer.locked=false;
                    layer.threeDLayer=true;layer.motionBlur=true;
                    layer.locked=locked;
                }
            }
        }
        comp.motionBlur=true;
        comp.shutterAngle=180;comp.shutterPhase=0;
        comp.motionBlurSamplesPerFrame=16;comp.motionBlurAdaptiveSampleLimit=128;
        var control=reuse ? oldControl : comp.layers.addNull(comp.duration);
        if(!reuse)control.name='Hook Zoom Out Control';control.threeDLayer=true;
        if(control.parent!==null)throw new Error('Camera control has a custom parent; integrate it explicitly');
        var fixed=control.property('ADBE Transform Group');
        var fixedNames=['ADBE Scale','ADBE Orientation','ADBE Rotate X','ADBE Rotate Y','ADBE Rotate Z'];
        var fixedValues=[[100,100,100],[0,0,0],0,0,0];
        for(var f=0;f<fixedNames.length;f++){
            var prop=fixed.property(fixedNames[f]);
            if(prop.numKeys || prop.expressionEnabled)
                throw new Error('Controller has custom scale/rotation animation; integrate it explicitly');
            prop.setValue(fixedValues[f]);
        }
        control.property('ADBE Transform Group').property('ADBE Anchor Point').setValue([0,0,0]);
        var pos=control.property('ADBE Transform Group').property('ADBE Position');
        if(!pos.dimensionsSeparated){
            pos.setValue([comp.width/2,comp.height/2,0]);pos.dimensionsSeparated=true;
        }
        var x=pos.getSeparationFollower(0), y=pos.getSeparationFollower(1);
        if(x.numKeys || y.numKeys || x.expressionEnabled || y.expressionEnabled)
            throw new Error('Existing controller has custom XY animation; integrate it explicitly');
        x.setValue(comp.width/2);y.setValue(comp.height/2);
        var z=pos.getSeparationFollower(2);
        if(z.expressionEnabled)throw new Error('Existing controller has a Z expression; merge it explicitly');
        if(reuse && !hasPlan){
            for(var prior=1;prior<=z.numKeys;prior++){
                if(z.keyTime(prior)<start-1e-7 || z.keyTime(prior)>end+1e-7)
                    throw new Error('Existing keys outside this range: supply a merged keyPlan; no previous range is deleted');
            }
        }
        while(z.numKeys>0)z.removeKey(z.numKeys);
        if(hasPlan){
            for(var m=0;m<opts.keyPlan.length;m++){
                var key=opts.keyPlan[m];
                z.setValueAtTime(key.time,key.z);
            }
        } else {
            z.setValueAtTime(start,travel);
            z.setValueAtTime(end,0);
        }
        for(var q=1;q<=z.numKeys;q++){
            z.setInterpolationTypeAtKey(q,KeyframeInterpolationType.BEZIER,KeyframeInterpolationType.BEZIER);
            z.setTemporalAutoBezierAtKey(q,false);
            z.setTemporalContinuousAtKey(q,false);
            z.setTemporalEaseAtKey(q,[new KeyframeEase(0,75)],[new KeyframeEase(0,75)]);
        }
        var camera=reuse ? oldCamera : comp.layers.addCamera('Hook Zoom Out Camera',[comp.width/2,comp.height/2]);
        // Camera layers are intrinsically 3D; there is no AV-layer 3D switch to set.
        camera.autoOrient=AutoOrientType.NO_AUTO_ORIENT;
        camera.parent=control;
        var tr=camera.property('ADBE Transform Group');
        tr.property('ADBE Position').setValue([0,0,-distance]);
        tr.property('ADBE Orientation').setValue([0,0,0]);
        tr.property('ADBE Rotate X').setValue(0);
        tr.property('ADBE Rotate Y').setValue(0);
        tr.property('ADBE Rotate Z').setValue(0);
        var settings=camera.property('ADBE Camera Options Group');
        settings.property('ADBE Camera Zoom').setValue(distance);
        settings.property('ADBE Camera Depth of Field').setValue(false);
        // Do NOT parent content to the moving camera control; doing so cancels zoom.
        camera.moveToBeginning();control.moveAfter(camera);
        comp.openInViewer();
        $.writeln('Hook Zoom Out: '+z.numKeys+' keys; returns to baseline at '+end+' seconds');
    } finally {app.endUndoGroup();}
}());
