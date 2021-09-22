#!/usr/bin/env python3

import sys
import os

import path_utils
import prjboot_util

import standard_c
import standard_cpp

def msvc15_solution_hex_id():
    sln_id = "8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942" # mvtodo
    return sln_id

def msvc15_prj_hex_id():
    prj_id = "7C79831C-A822-47F3-B80A-66BEB3F427A1" # mvtodo
    return prj_id

def msvc15slnfile_contents(project_name):

    r = ""
    r += "\nMicrosoft Visual Studio Solution File, Format Version 12.00\n"
    r += "# Visual Studio 15\n"
    r += "VisualStudioVersion = 15.0.26228.9\n"
    r += "MinimumVisualStudioVersion = 10.0.40219.1\n"
    r += "Project(\"{%s}\") = \"%s\", \"%s.vcxproj\", \"{%s}\"\n" % (msvc15_solution_hex_id(), project_name, project_name, msvc15_prj_hex_id())
    r += "EndProject\n"
    r += "Global\n"
    r += "\tGlobalSection(SolutionConfigurationPlatforms) = preSolution\n"
    r += "\t\tDebug|x64 = Debug|x64\n"
    r += "\t\tRelease|x64 = Release|x64\n"
    r += "\tEndGlobalSection\n"
    r += "\tGlobalSection(ProjectConfigurationPlatforms) = postSolution\n"
    r += "\t\t{%s}.Debug|x64.ActiveCfg = Debug|x64\n" % msvc15_prj_hex_id()
    r += "\t\t{%s}.Debug|x64.Build.0 = Debug|x64\n" % msvc15_prj_hex_id()
    r += "\t\t{%s}.Release|x64.ActiveCfg = Release|x64\n" % msvc15_prj_hex_id()
    r += "\t\t{%s}.Release|x64.Build.0 = Release|x64\n" % msvc15_prj_hex_id()
    r += "\tEndGlobalSection\n"
    r += "\tGlobalSection(SolutionProperties) = preSolution\n"
    r += "\t\tHideSolutionNode = FALSE\n"
    r += "\tEndGlobalSection\n"
    r += "EndGlobal\n"

    ba_r = bytearray(b"\xEF\xBB\xBF")
    ba_r.extend(map(ord, r))
    return ba_r

def msvc15projfile_contents(project_name):

    # mvtodo: cpp compiler flags (debug/release/windows) {msvc compiler} and cpp linker flags (debug/release) {msvc compiler}

    r = ""
    r += "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
    r += "<Project DefaultTargets=\"Build\" ToolsVersion=\"15.0\" xmlns=\"http://schemas.microsoft.com/developer/msbuild/2003\">\n"
    r += "  <ItemGroup Label=\"ProjectConfigurations\">\n"
    r += "    <ProjectConfiguration Include=\"Debug|x64\">\n"
    r += "      <Configuration>Debug</Configuration>\n"
    r += "      <Platform>x64</Platform>\n"
    r += "    </ProjectConfiguration>\n"
    r += "    <ProjectConfiguration Include=\"Release|x64\">\n"
    r += "      <Configuration>Release</Configuration>\n"
    r += "      <Platform>x64</Platform>\n"
    r += "    </ProjectConfiguration>\n"
    r += "  </ItemGroup>\n"
    r += "  <PropertyGroup Label=\"Globals\">\n"
    r += "    <VCProjectVersion>15.0</VCProjectVersion>\n"
    r += "    <ProjectGuid>{%s}</ProjectGuid>\n" % msvc15_prj_hex_id()
    r += "    <RootNamespace>%s</RootNamespace>\n" % project_name
    r += "    <WindowsTargetPlatformVersion>10.0.14393.0</WindowsTargetPlatformVersion>\n"
    r += "  </PropertyGroup>\n"
    r += "  <Import Project=\"$(VCTargetsPath)\Microsoft.Cpp.Default.props\" />\n"
    r += "  <PropertyGroup Condition=\"\'$(Configuration)|$(Platform)\'==\'Debug|x64\'\" Label=\"Configuration\">\n"
    r += "    <ConfigurationType>Application</ConfigurationType>\n"
    r += "    <UseDebugLibraries>true</UseDebugLibraries>\n"
    r += "    <PlatformToolset>v141</PlatformToolset>\n"
    r += "    <CharacterSet>MultiByte</CharacterSet>\n"
    r += "  </PropertyGroup>\n"
    r += "  <PropertyGroup Condition=\"\'$(Configuration)|$(Platform)\'==\'Release|x64\'\" Label=\"Configuration\">\n"
    r += "    <ConfigurationType>Application</ConfigurationType>\n"
    r += "    <UseDebugLibraries>false</UseDebugLibraries>\n"
    r += "    <PlatformToolset>v141</PlatformToolset>\n"
    r += "    <WholeProgramOptimization>true</WholeProgramOptimization>\n"
    r += "    <CharacterSet>MultiByte</CharacterSet>\n"
    r += "  </PropertyGroup>\n"
    r += "  <Import Project=\"$(VCTargetsPath)\Microsoft.Cpp.props\" />\n"
    r += "  <ImportGroup Label=\"ExtensionSettings\">\n"
    r += "  </ImportGroup>\n"
    r += "  <ImportGroup Label=\"Shared\">\n"
    r += "  </ImportGroup>\n"
    r += "  <ImportGroup Label=\"PropertySheets\" Condition=\"\'$(Configuration)|$(Platform)\'==\'Debug|x64\'\">\n"
    r += "    <Import Project=\"$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props\" Condition=\"exists(\'$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props\')\" Label=\"LocalAppDataPlatform\" />\n"
    r += "  </ImportGroup>\n"
    r += "  <ImportGroup Label=\"PropertySheets\" Condition=\"\'$(Configuration)|$(Platform)\'==\'Release|x64\'\">\n"
    r += "    <Import Project=\"$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props\" Condition=\"exists(\'$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props\')\" Label=\"LocalAppDataPlatform\" />\n"
    r += "  </ImportGroup>\n"
    r += "  <PropertyGroup Label=\"UserMacros\" />\n"
    r += "  <PropertyGroup Condition=\"\'$(Configuration)|$(Platform)\'==\'Release|x64\'\">\n"
    r += "    <OutDir>$(SolutionDir)..\\..\\run\windows_$(PlatformTarget)_$(Configuration)\\</OutDir>\n"
    r += "    <IntDir>$(SolutionDir)..\\..\\build\windows_$(PlatformTarget)_$(Configuration)\\</IntDir>\n"
    r += "  </PropertyGroup>\n"
    r += "  <PropertyGroup Condition=\"\'$(Configuration)|$(Platform)\'==\'Debug|x64\'\">\n"
    r += "    <OutDir>$(SolutionDir)..\\..\\run\\windows_$(PlatformTarget)_$(Configuration)\\</OutDir>\n"
    r += "    <IntDir>$(SolutionDir)..\\..\\build\\windows_$(PlatformTarget)_$(Configuration)\\</IntDir>\n"
    r += "  </PropertyGroup>\n"
    r += "  <ItemDefinitionGroup Condition=\"\'$(Configuration)|$(Platform)\'==\'Debug|x64\'\">\n"
    r += "    <ClCompile>\n"
    r += "      <WarningLevel>Level3</WarningLevel>\n"
    r += "      <Optimization>Disabled</Optimization>\n"
    r += "      <SDLCheck>true</SDLCheck>\n"
    r += "    </ClCompile>\n"
    r += "  </ItemDefinitionGroup>\n"
    r += "  <ItemDefinitionGroup Condition=\"\'$(Configuration)|$(Platform)\'==\'Release|x64\'\">\n"
    r += "    <ClCompile>\n"
    r += "      <WarningLevel>Level3</WarningLevel>\n"
    r += "      <Optimization>MaxSpeed</Optimization>\n"
    r += "      <FunctionLevelLinking>true</FunctionLevelLinking>\n"
    r += "      <IntrinsicFunctions>true</IntrinsicFunctions>\n"
    r += "      <SDLCheck>true</SDLCheck>\n"
    r += "    </ClCompile>\n"
    r += "    <Link>\n"
    r += "      <EnableCOMDATFolding>true</EnableCOMDATFolding>\n"
    r += "      <OptimizeReferences>true</OptimizeReferences>\n"
    r += "    </Link>\n"
    r += "  </ItemDefinitionGroup>\n"
    #r += "  <ItemGroup>\n"
    #r += "    <ClInclude Include=\"..\\..\\include\\example.h\" />\n" # mvtodo
    #r += "  </ItemGroup>\n"
    r += "  <ItemGroup>\n"
    r += "    <ClCompile Include=\"..\\..\\src\\main.cpp\" />\n"
    r += "  </ItemGroup>\n"
    r += "  <Import Project=\"$(VCTargetsPath)\\Microsoft.Cpp.targets\" />\n"
    r += "  <ImportGroup Label=\"ExtensionTargets\">\n"
    r += "  </ImportGroup>\n"
    r += "</Project>\n"

    ba_r = bytearray(b"\xEF\xBB\xBF")
    ba_r.extend(map(ord, r))
    return ba_r

def generate_c_msvc_15(target_dir, project_name):
    return False, "mvtodo"

def generate_cpp_msvc_15(target_dir, project_name):

    # base folders / base structure
    prj_fullname_base = path_utils.concat_path(target_dir, project_name)
    base_prj = path_utils.concat_path(prj_fullname_base, "proj")

    base_build = path_utils.concat_path(prj_fullname_base, "build")
    base_build_windows_x64_debug = path_utils.concat_path(base_build, "windows_x64_debug")
    base_build_windows_x64_release = path_utils.concat_path(base_build, "windows_x64_release")

    base_run = path_utils.concat_path(prj_fullname_base, "run")
    base_run_windows_x64_debug = path_utils.concat_path(base_run, "windows_x64_debug")
    base_run_windows_x64_release = path_utils.concat_path(base_run, "windows_x64_release")

    base_src = path_utils.concat_path(prj_fullname_base, "src")

    prjboot_util.makedir_if_needed(prj_fullname_base)
    prjboot_util.makedir_if_needed(base_prj)

    prjboot_util.makedir_if_needed(base_build)
    prjboot_util.makedir_if_needed(base_build_windows_x64_debug)
    prjboot_util.makedir_if_needed(base_build_windows_x64_release)

    prjboot_util.makedir_if_needed(base_run)
    prjboot_util.makedir_if_needed(base_run_windows_x64_debug)
    prjboot_util.makedir_if_needed(base_run_windows_x64_release)

    prjboot_util.makedir_if_needed(base_src)

    # generate the actual C++ Visual Studio project and solution files
    base_prj_msvc15 = path_utils.concat_path(base_prj, "msvc15_cpp")
    os.mkdir(base_prj_msvc15)
    base_prj_msvc15_sln = path_utils.concat_path(base_prj_msvc15, "%s.sln" % project_name)
    base_prj_msvc15_fn = path_utils.concat_path(base_prj_msvc15, "%s.vcxproj" % project_name)
    prjboot_util.writecontents(base_prj_msvc15_sln, msvc15slnfile_contents(project_name))
    prjboot_util.writecontents(base_prj_msvc15_fn, msvc15projfile_contents(project_name))

    # main C++ file
    base_src_main_cpp_fn = path_utils.concat_path(base_src, "main.cpp")
    if not prjboot_util.writecontents(base_src_main_cpp_fn, standard_cpp.get_main_cpp_app()):
        return False, "Failed creating [%s]" % base_src_main_cpp_fn

    # secondary C++ file
    base_src_subfolder = path_utils.concat_path(base_src, "subfolder")
    prjboot_util.makedir_if_needed(base_src_subfolder)
    base_src_subfolder_secondary_cpp_fn = path_utils.concat_path(base_src_subfolder, "second.cpp")
    if not prjboot_util.writecontents(base_src_subfolder_secondary_cpp_fn, prjboot_util.secondary_c_app()):
        return False, "Failed creating [%s]" % base_src_subfolder_secondary_cpp_fn

    # gitignore
    gitignore_filename = path_utils.concat_path(prj_fullname_base, ".gitignore")
    prjboot_util.add_to_gitignore_if_needed(gitignore_filename, "build/")
    prjboot_util.add_to_gitignore_if_needed(gitignore_filename, "run/")
    prjboot_util.add_to_gitignore_if_needed(gitignore_filename, "proj/msvc15_cpp/.vs")
    prjboot_util.add_to_gitignore_if_needed(gitignore_filename, "proj/msvc15_cpp/%s.VC.db" % project_name)
    prjboot_util.add_to_gitignore_if_needed(gitignore_filename, "proj/msvc15_cpp/%s.vcxproj.user" % project_name)

    return True, None
