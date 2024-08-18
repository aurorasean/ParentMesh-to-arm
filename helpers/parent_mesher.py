import bpy
import bmesh
import json
from ..merge_order import MergeOrder, DataHold
from ..bone_helper import BoneHelper
from ..scene_helper import SceneHelper
import re


class ParentMergeOrder:
    def __init__(self, parent, mergeOrders):
        self.parent = parent
        self.mergeOrders = mergeOrders


class ActionHolder:
    def __init__(self, name, action):
        self.name = name
        self.action = action


class ParentChild:
    rootBoneName = None

    def __init__(self, parent, childs):
        self.parent = parent
        self.childs = childs


class Parent_Mesher(bpy.types.Operator):
    bl_idname = "view3d.parent_mesh_armature"
    bl_label = "Parent mesh to Armature"
    bl_description = "Parent to mesh armature"
    index = 0
    bone_prefix = "bn_"
    root_prefix = "rt_"
    allowedTypes = ["MESH", "ARMATURE"]
    meshTypes = ["MESH"]
    actionsStored: list[ActionHolder] = []

    # Get roots
    def returnChilds(self, obj):
        parentChild = []
        if obj.children:
            for child in obj.children:
                if child.children:
                    parentChild.append(
                        ParentChild(child.name, [self.returnChilds(child)])
                    )
                else:
                    parentChild.append(ParentChild(child.name, []))
        return ParentChild(obj.name, parentChild)

    def getDictChildren(self) -> list[ParentChild]:
        data = []
        for obj in bpy.data.objects:
            if (
                obj.visible_get()
                and str(obj.type) in self.allowedTypes
                and obj.parent is None
                and len(obj.children) > 0
            ):
                pc = self.returnChilds(obj)
                data.append(pc)

                SceneHelper.selectObject(obj.name)
                parentLocation = obj.matrix_world.to_translation()
                bpy.ops.transform.translate(
                    value=(
                        parentLocation[0] * -1,
                        parentLocation[1] * -1,
                        parentLocation[2] * -1,
                    )
                )

        for rootDD in data:
            rootBoneName = self.createRootArmature(rootDD)
            rootDD.rootBoneName = rootBoneName
            # Do stuff here
        return data

    def createRootArmature(self, rootName):
        root = bpy.data.objects[rootName.parent]
        rootLocation = root.matrix_world.to_translation()
        bpy.ops.object.armature_add(
            enter_editmode=False, align="WORLD", location=rootLocation, scale=(1, 1, 1)
        )
        SceneHelper.getSelected().name = "%s%s" % (self.root_prefix, root.name)
        childBoneName = SceneHelper.getSelected().name
        arm_obj = bpy.data.objects[childBoneName]
        bpy.context.view_layer.objects.active = arm_obj
        bpy.ops.object.mode_set(mode="EDIT")
        edit_bones = arm_obj.data.edit_bones
        edit_bones[0].name = "%s%s" % (self.bone_prefix, root.name)
        bpy.ops.object.mode_set(mode="OBJECT")
        SceneHelper.unselectAll()
        return childBoneName

    def add_root_bone_merge(self, mergeOrders: list[MergeOrder], parent: ParentChild):
        parent = SceneHelper.getObject(parent.parent)

        parentDataHold = DataHold(
            parent.name,
            True if parent.type in self.meshTypes else False,
            "%s%s" % (self.bone_prefix, parent.name),
        )
        parentDataHold.boneNameLink = "%s%s" % (parentDataHold.name, "_link")

        mergeOrders.append(MergeOrder(parentDataHold, parentDataHold, 0, 0))

    # Get roots
    # Get Merge order
    def filterMergeOrder(self, mergeOrder: MergeOrder):
        return (
            mergeOrder.child.name != ""
            and mergeOrder.child.name != mergeOrder.parent.name
        )

    def getMergerOrder(
        self, parentName: str, mergeOrder, child: ParentChild, rootLevel
    ):
        if len(child.childs) > 0:
            for childInner in child.childs:
                if child.parent != childInner:
                    self.index += 1
                    tempRootLevel = rootLevel + 1
                    mergeOrder + self.getMergerOrder(
                        child.parent, mergeOrder, childInner, tempRootLevel
                    )
        self.index += 1

        parent = SceneHelper.getObject(parentName)
        parentBoneName = "%s%s" % (self.bone_prefix, parent.name)
        parentIsMesh = True if parent.type in self.meshTypes else False

        child = SceneHelper.getObject(child.parent)
        childBoneName = "%s%s" % (self.bone_prefix, child.name)
        childtIsMesh = True if child.type in self.meshTypes else False

        parentDataHold = DataHold(parent.name, parentIsMesh, parentBoneName)
        childDataHold = DataHold(child.name, childtIsMesh, childBoneName)

        mergeOrder.append(
            MergeOrder(parentDataHold, childDataHold, self.index, rootLevel)
        )
        return mergeOrder

    def get_parent_merge_order(self, parent) -> list[MergeOrder]:

        mergeOrder: list[MergeOrder] = []
        if len(parent.childs) > 0:
            for child in parent.childs:
                # repeat
                mergeOrder + self.getMergerOrder(parent.parent, mergeOrder, child, 1)

        validMerges: list[MergeOrder] = sorted(
            filter(self.filterMergeOrder, mergeOrder),
            key=lambda x: x.get_index(),
            reverse=True,
        )
        return validMerges

    # Get Merge order
    def assign_object_constraints(
        self, mergeOrders: list[MergeOrder], parent: ParentChild
    ):
        SceneHelper.unselectAll()
        for mergeOrder in mergeOrders:
            if mergeOrder.child.isMesh:
                child = SceneHelper.selectObject(mergeOrder.child.originalName)
                # child.constraint_add(type='ARMATURE')
                child.constraints.new("ARMATURE")
                child.constraints["Armature"].targets.new()
                child.constraints["Armature"].targets[0].target = bpy.data.objects[
                    parent.rootBoneName
                ]
                child.constraints["Armature"].targets[
                    0
                ].subtarget = mergeOrder.child.boneName
                # bpy.ops.outliner.parent_clear()
                child.parent = None
                SceneHelper.unselectAll()
                pass
            pass
        pass

    def assign_vertex_groups(self, mergeOrders: list[MergeOrder]):
        for mergeOrder in mergeOrders:
            if mergeOrder.child.isMesh:
                child = SceneHelper.selectObject(mergeOrder.child.name)
                if len(child.vertex_groups) == 0 and child.visible_get():
                    bpy.context.view_layer.objects.active = child
                    bpy.ops.object.editmode_toggle()

                    mesh = bmesh.from_edit_mesh(child.data)
                    for v in mesh.verts:
                        v.select = True
                    # bpy.ops.object.mode_set(mode='EDIT')

                    listVerts = []
                    for vert in bpy.context.object.data.vertices:
                        listVerts.append(vert.index)

                    bpy.ops.object.editmode_toggle()
                    group = child.vertex_groups.new()
                    group.name = mergeOrder.child.boneName
                    child.vertex_groups[group.name].add(listVerts, 1, "REPLACE")
            # if mergeOrder.isMesh:

    # Create Bones
    def getGlobalBonePoint(self, childLocation, boneLocation):
        xVert = childLocation[0] + boneLocation[0]
        yVert = childLocation[1] + boneLocation[1]
        zVert = childLocation[2] + boneLocation[2]
        return (xVert, yVert, zVert)

    def getBoneLocationAndDelete(self, childName):
        arm_obj = bpy.data.objects[childName]
        bpy.context.view_layer.objects.active = arm_obj
        test = arm_obj.matrix_world.to_translation()
        newLocation = (test[0], test[1], test[2])
        bpy.ops.object.mode_set(mode="EDIT")

        firstBoneHeadLocation = self.getGlobalBonePoint((0, 0, 0), newLocation)
        firstBoneTailLocation = self.getGlobalBonePoint(
            (0, 0, 0), self.getGlobalBonePoint(newLocation, (0, 0, 1))
        )
        print("First armobj %s" % arm_obj.location)
        print(
            "First newLocation %s, %s, %s"
            % (newLocation[0], newLocation[1], newLocation[2])
        )
        print("First Bone Head %s" % firstBoneHeadLocation[0])
        print("First Bone Tail %s" % firstBoneTailLocation[0])
        print("First Bone Head %s" % firstBoneHeadLocation[1])
        print("First Bone Tail %s" % firstBoneTailLocation[1])
        print("First Bone Head %s" % firstBoneHeadLocation[2])
        print("First Bone Tail %s" % firstBoneTailLocation[2])

        bpy.ops.object.mode_set(mode="OBJECT")
        SceneHelper.unselectAll()
        childDelete = SceneHelper.selectObject(childName)
        bpy.context.view_layer.objects.active = childDelete
        bpy.ops.object.delete(use_global=False, confirm=False)
        return [firstBoneHeadLocation, firstBoneTailLocation]

    def checkIfVertInTheSamePlaceAndCorrect(self, current, addVert):
        if (
            current[0] == addVert[0]
            and current[1] == addVert[1]
            and current[2] == addVert[2]
        ):
            return (current[0], current[1], current[2] + 0.01)
        return current

    def storeAnimationData(self, action, elementName):
        # store the animation data
        self.actionsStored.append(ActionHolder(elementName, action))

    def create_and_parent_bones(self, mergeOrders: list[MergeOrder], rootBoneName: str):
        for merge in mergeOrders:
            print("==============================================")
            print("Parent %s" % merge.parent.name)
            print("Child %s" % merge.child.name)
            parent = SceneHelper.getObject(merge.parent.name)
            parentLocation = parent.matrix_world.to_translation()

            child = SceneHelper.getObject(merge.child.name)
            childLocation = child.matrix_world.to_translation()

            childBoneNameLink = "%s%s" % (merge.child.boneName, "_link")
            merge.child.boneNameLink = childBoneNameLink

            # check if the child has an animation
            # actions = bpy.data.actions.keys()
            # if child.animation_data is not None:
            #     if child.animation_data.action is not None:
            #         print("Action %s" % child.animation_data.action.name)
            #         # copy the animation data into the self
            #         self.storeAnimationData(child.animation_data.action, child.name)
            #         # actions.append(child.animation_data.action.name)

            childBoneDetails = []

            if not merge.child.isMesh:
                # delete and recreate the bone
                childBoneDetails = self.getBoneLocationAndDelete(merge.child.name)
            else:
                childBoneDetails = [
                    childLocation,
                    (childLocation[0], childLocation[1], childLocation[2] + 1),
                ]
            # note: when copy arm, get it's location and add (+) the x,y,z
            #  And set it's location!

            arm_obj = bpy.data.objects[rootBoneName]
            bpy.context.view_layer.objects.active = arm_obj
            bpy.ops.object.mode_set(mode="EDIT")
            edit_bones = arm_obj.data.edit_bones

            boneChildExists = BoneHelper.doesBoneExist(edit_bones, merge.child.boneName)
            boneChild = None
            if boneChildExists:
                print("Bone Exists %s" % merge.child.boneName)
                boneChild = edit_bones[merge.child.boneName]

            if boneChild == None:
                print("Bone Does not exist %s" % merge.child.boneName)
                boneChild = edit_bones.new(merge.child.boneName)
                boneChild.head = childBoneDetails[0]
                boneChild.tail = childBoneDetails[1]

            boneChildLink = edit_bones.new(childBoneNameLink)
            boneChildLink.head = parentLocation
            boneChildLink.tail = self.checkIfVertInTheSamePlaceAndCorrect(
                childLocation, parentLocation
            )
            for bbone in edit_bones:
                BoneHelper.boneSelect(bbone, False)

            BoneHelper.boneSelect(boneChildLink, True)
            BoneHelper.boneSelect(boneChild, True)
            boneChild.parent = boneChildLink

            bpy.ops.object.mode_set(mode="OBJECT")
            SceneHelper.unselectAll()
            print("==============================================")

    def parent_links_to_bone(self, mergeOrders: list[MergeOrder], parent: ParentChild):
        arm_obj = bpy.data.objects[parent.rootBoneName]
        for merge in mergeOrders:
            if merge.index != 0:
                parentBone = merge.parent.boneName
                childBone = merge.child.boneNameLink

                bpy.context.view_layer.objects.active = arm_obj
                bpy.ops.object.mode_set(mode="EDIT")
                edit_bones = arm_obj.data.edit_bones
                pBone = edit_bones[parentBone]
                if not childBone in edit_bones:
                    print("Bone %s does not exist" % childBone)

                    continue

                cBone = edit_bones[childBone]

                BoneHelper.boneSelect(cBone, True)
                BoneHelper.boneSelect(pBone, True)

                cBone.parent = pBone
                bpy.ops.object.mode_set(mode="OBJECT")
                SceneHelper.unselectAll()

    def merge_mesh_together(self, mergeOrders: list[MergeOrder], parent: ParentChild):
        parentObj = SceneHelper.getObject(parent.parent)
        parentLocation = parentObj.matrix_world.to_translation()

        SceneHelper.unselectAll()
        for merge in mergeOrders:
            if merge.child.isMesh:
                SceneHelper.selectObject(merge.child.name)

        bpy.context.view_layer.objects.active = parentObj

        bpy.ops.object.join()

        newParent = SceneHelper.getSelected()
        newParent.name = parent.parent
        saved_location = bpy.context.scene.cursor.location

        bpy.context.scene.cursor.location = parentLocation
        bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
        bpy.context.scene.cursor.location = saved_location

        SceneHelper.unselectAll()

    def parent_mesh_to_arm(self, parent: ParentChild):
        SceneHelper.selectObject(parent.parent)
        arm = SceneHelper.selectObject(parent.rootBoneName)
        bpy.context.view_layer.objects.active = arm
        bpy.ops.object.parent_set(type="ARMATURE")
        SceneHelper.unselectAll()

    def create_stand_in_planes(self, mergeOrders: list[MergeOrder]):
        for merge in mergeOrders:
            if merge.child.isMesh:
                SceneHelper.selectObject(merge.child.name)
                selected = SceneHelper.getSelected()
                bpy.ops.view3d.snap_cursor_to_selected()
                locationNew = bpy.context.scene.cursor.location
                bpy.ops.mesh.primitive_plane_add(
                    size=selected.dimensions[0],
                    enter_editmode=False,
                    align="WORLD",
                    location=(locationNew[0], locationNew[1], locationNew[2]),
                    scale=(1, 1, 1),
                )
                bpy.context.object.name = "standin_%s" % merge.child.name
                merge.child.originalName = merge.child.name
                # replace name of the stand in
                merge.child.name = bpy.context.object.name
                SceneHelper.unselectAll()

    def assign_animation_data(self, parent: ParentChild):
        print("Actions %s" % self.actionsStored)
        parentArm = SceneHelper.getObject(parent.rootBoneName)
        print("Parent Arm %s" % parentArm)
        parentArm.animation_data_create()
        parentFcurve = None

        bpy.ops.object.posemode_toggle()
        bones = bpy.data.objects[parentArm.name].data.bones

        for idx, bone in enumerate(bones):
            # find the action for this bone from the stored
            # get orginal bone from actions stored

            originalBone = next(
                (
                    d
                    for d in self.actionsStored
                    if d.name == bone.name.replace("bn_", "")
                ),
                None,
            )
            if originalBone is None:
                continue
            cleanedCurves = []
            # (pose.bones\[")(.*)("\].)(.*)
            regex = re.compile(r'(pose.bones\[")(.*)("\].)(.*)', re.IGNORECASE)

            for fcurve in list(originalBone.action.fcurves):
                data_name_clean = ""
                match = regex.match(fcurve.data_path)
                if match:
                    boneNameRe = regex.match(fcurve.data_path).group(2)
                    if boneNameRe is not None:
                        data_name_clean = boneNameRe
                else:
                    data_name_clean = (
                        fcurve.data_path.replace("location", "")
                        .replace("rotation_euler", "")
                        .replace("scale", "")
                        .replace("rotation_quaternion", "")
                    )
                fcurve.data_path = data_name_clean
                currentlyAdded = next(
                    (d for d in cleanedCurves if d.data_path == fcurve.data_path),
                    None,
                )
                if currentlyAdded is None:
                    cleanedCurves.append(fcurve)

            for fcurve in cleanedCurves:
                # each curve is a animation line
                # this is a pose bone animation, check for the correct one by name
                if bone.name.replace("bn_", "") in fcurve.data_path:

                    continue
                else:
                    # just a normal animation
                    pass
                pass
                # for each frame in the action
            print("Original Bone %s" % originalBone.name)
            #
            pass
        # for action in self.actionsStored:
        #     if action is not None:
        #         if parentArm.animation_data.action is None:
        #             parentArm.animation_data_create()
        #             parentFcurve = parentArm.animation_data.action.fcurves.new(
        #                 data_path="rotation_euler", index=2
        #             )
        #         orgCurve = action.action.fcurves

        #         for curve in orgCurve:
        #             parentFcurve.animation_data.action.fcurves.new(
        #                 data_path=curve.data_path, index=curve.array_index
        #             )
        #         parentArm.animation_data.action.name = action.name
        #         parentArm.animation_data.action.use_fake_user = True
        #         parentArm.animation_data.action.use_nla = True

        #         # create an action on the parent
        #         # then create a group under action.groups to hold the actual anim data

        #         # need to find the bone that has to be applied to

        #         print("Action %s" % action.name)
        #         # find the bone that was used in the animation
        #         pass

    def link_object_to_collection(self, obj, col):
        bpy.data.collections[col].objects.link(obj)

    def collection_exists(self, col: str):
        return col in bpy.data.collections

    def recurLayerCollection(self, layerColl, collName):
        found = None
        if layerColl.name == collName:
            return layerColl
        for layer in layerColl.children:
            found = self.recurLayerCollection(layer, collName)
            if found:
                return found

    def selectCollection(self, name):
        col = bpy.data.collections[name]
        bpy.context.view_layer.active_layer_collection = col

    def create_collection(self, name):
        if not self.collection_exists(name):
            bpy.data.collections.new(name)
            colref = bpy.data.collections[name]
            # cant select the collection...

            # bpy.context.collection = colref
            # bpy.ops.collection.exporter_add(name="IO_FH_gltf2")
            # colref.exporters[0] = bpy.data.collections['Collection'].exporters[0]
            # self.selectCollection(name)
            bpy.context.scene.collection.children.link(colref)
            return colref
        return False

    def clear_animation_data(self, mergeOrders: list[MergeOrder]):
        for merge in mergeOrders:
            if merge.child.isMesh:
                SceneHelper.selectObject(merge.child.originalName)
                obj = SceneHelper.getSelected()
                if obj.animation_data is not None:
                    obj.animation_data.action = None
                SceneHelper.unselectAll()
    
    def recurLayerCollection(self, layerColl, collName):
        found = None
        if (layerColl.name == collName):
            return layerColl
        for layer in layerColl.children:
            found = self.recurLayerCollection(layer, collName)
            if found:
                return found
    def selectCollectionByObject(self, obj, colName, path):
        SceneHelper.selectObject(obj.name)
        obj = SceneHelper.getSelected()
        ucol = obj.users_collection
        
        targetCol = next(
            (
                d
                for d in ucol
                if d.name == colName
            ),
            None,
        )

        #Switching active Collection to active Object selected
        layer_collection = bpy.context.view_layer.layer_collection
        layerColl = self.recurLayerCollection(layer_collection, targetCol.name)
        bpy.context.view_layer.active_layer_collection = layerColl
        # update the exporter!
        bpy.ops.collection.exporter_add(name="IO_FH_gltf2")
        bpy.data.collections[colName].exporters[0].export_properties.filepath=path
        SceneHelper.unselectAll()
        pass
    def move_to_collections(self, mergeOrders: list[MergeOrder], parent: ParentChild):
        self.create_collection("Meshes")
        self.create_collection("Skeletons")
        SceneHelper.unselectAll()
        firstMeshObject = None
        firstSkelObject = None
        for merge in mergeOrders:
            meshes = [merge.child.name, merge.child.originalName]
            for meshname in meshes:
                if "standin" in meshname:
                    SceneHelper.selectObject(merge.child.name)
                    obj = SceneHelper.getSelected()
                    self.link_object_to_collection(obj, "Skeletons")
                    SceneHelper.unselectAll()
                    if firstSkelObject is None:
                        firstSkelObject = obj
                else:
                    if not merge.child.isMesh and not SceneHelper.doesObjectExist(
                        merge.child.name
                    ):
                        continue
                    else:
                        SceneHelper.selectObject(meshname)
                        obj = SceneHelper.getSelected()
                        if firstMeshObject is None:
                            firstMeshObject = obj
                        self.link_object_to_collection(obj, "Meshes")
                        SceneHelper.unselectAll()
            SceneHelper.unselectAll()

        SceneHelper.selectObject(parent.rootBoneName)
        obj = SceneHelper.getSelected()
        self.link_object_to_collection(obj, "Skeletons")
        SceneHelper.unselectAll()
        if firstSkelObject is None:
            firstSkelObject = obj
        fileNameExport = bpy.path.basename(bpy.context.blend_data.filepath).replace('.blend', '')
        self.selectCollectionByObject(firstMeshObject, 'Meshes', f"//{fileNameExport}-mesh.gltf")
        self.selectCollectionByObject(firstSkelObject, 'Skeletons', f"//{fileNameExport}-skel.gltf")
        # update the collections for new exporter

    def move_to_origin(self, mergeOrders: list[MergeOrder], movetoOrigin: bool):
        if movetoOrigin:
            SceneHelper.unselectAll()
            # change sort order
            mergeOrdersTemp = sorted(
                mergeOrders, key=lambda x: x.get_index(), reverse=False
            )
            for merge in mergeOrdersTemp:
                print("Merge %s" % merge.child.originalName)
                if merge.child.isMesh:
                    SceneHelper.selectObject(merge.child.originalName)
                    obj = SceneHelper.getSelected()
                    location = obj.matrix_world.to_translation()
                    print("Location %s %s" % (location, obj.name))

                    print("Object keys:", obj.keys())
                    bpy.ops.transform.translate(
                        value=(
                            location[0] * -1,
                            location[1] * -1,
                            location[2] * -1,
                        )
                    )
                    bpy.context.view_layer.objects.active = SceneHelper.getSelected()
                    bpy.ops.object.transform_apply(
                        location=True, rotation=True, scale=True
                    )
                    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
                    bpy.ops.object.transform_apply(
                        location=True, rotation=True, scale=True
                    )
                    SceneHelper.unselectAll()

    def execute(self, context):
        # reset the actions stored
        self.actionsStored = []

        if len(SceneHelper.getSelectedObjects()) <= 0:
            SceneHelper.unselectAll()
            bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.transforms_to_deltas(mode="ALL")
        # bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        createSkin = context.scene.createSkin
        movetoOrigin = context.scene.movetoOrigin
        print("createSkin %s" % createSkin)
        dictchild = self.getDictChildren()
        for parent in dictchild:
            print("---------------------------------------------")
            print("Starting %s" % parent.rootBoneName)
            mergeOrders = self.get_parent_merge_order(parent)
            self.add_root_bone_merge(mergeOrders, parent)

            mergeOrders = sorted(mergeOrders, key=lambda x: x.get_index(), reverse=True)

            self.create_and_parent_bones(mergeOrders, parent.rootBoneName)
            self.parent_links_to_bone(mergeOrders, parent)
            if not createSkin:
                # create stand in planes
                self.create_stand_in_planes(mergeOrders)
                parent.parent = "standin_%s" % parent.parent

                self.assign_vertex_groups(mergeOrders)
                self.assign_object_constraints(mergeOrders, parent)
                self.move_to_collections(mergeOrders, parent)
            else:
                self.assign_vertex_groups(mergeOrders)

            self.move_to_origin(mergeOrders, movetoOrigin)

            self.merge_mesh_together(mergeOrders, parent)
            self.parent_mesh_to_arm(parent)
            print("---------------------------------------------")
            print("Finished %s" % parent.rootBoneName)
        print("Finished")
        return {"FINISHED"}
