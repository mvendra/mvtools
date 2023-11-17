#!/usr/bin/env python3

import sys
import os

import path_utils
import prjboot_util

import standard_c

def codelite15_c_projfile_contents(project_name):

    r = ""

    r += "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
    r += "<CodeLite_Project Name=\"%s\" Version=\"11000\" InternalType=\"Console\">\n" % project_name
    r += "  <Description/>\n"
    r += "  <Dependencies/>\n"
    r += "  <VirtualDirectory Name=\"src\">\n"
    r += "    <VirtualDirectory Name=\"subfolder\">\n"
    r += "      <File Name=\"../../src/subfolder/second.c\"/>\n"
    r += "    </VirtualDirectory>\n"
    r += "    <File Name=\"../../src/main.c\"/>\n"
    r += "  </VirtualDirectory>\n"
    r += "  <Dependencies Name=\"Linux / x64 / Debug\"/>\n"
    r += "  <Dependencies Name=\"Linux / x64 / Release\"/>\n"
    r += "  <Settings Type=\"Executable\">\n"
    r += "    <GlobalSettings>\n"
    r += "      <Compiler Options=\"\" C_Options=\"\" Assembler=\"\">\n"
    r += "        <IncludePath Value=\".\"/>\n"
    r += "      </Compiler>\n"
    r += "      <Linker Options=\"\">\n"
    r += "        <LibraryPath Value=\".\"/>\n"
    r += "      </Linker>\n"
    r += "      <ResourceCompiler Options=\"\"/>\n"
    r += "    </GlobalSettings>\n"

    r += "    <Configuration Name=\"Linux / x64 / Debug\" CompilerType=\"GCC\" DebuggerType=\"GNU gdb debugger\" Type=\"Executable\" BuildCmpWithGlobalSettings=\"append\" BuildLnkWithGlobalSettings=\"append\" BuildResWithGlobalSettings=\"append\">\n"
    r += "      <Compiler Options=\"-g;-O0;-Wall\" C_Options=\"%s\" Assembler=\"\" Required=\"yes\" PreCompiledHeader=\"\" PCHInCommandLine=\"no\" PCHFlags=\"\" PCHFlagsPolicy=\"0\">\n" % prjboot_util.inline_opts(";", standard_c.get_c_compiler_flags_debug_gcc() + standard_c.get_c_compiler_flags_linux_gcc())
    r += "      </Compiler>\n"
    r += "      <Linker Options=\"\" Required=\"yes\">\n"
    r += prjboot_util.deco_if_not_empty("", prjboot_util.format_xml_tag_value_list("        ", "Library", "Value", standard_c.get_c_linker_flags_debug_gcc(), prjboot_util.filter_remove_dash_l), "\n")
    r += "      </Linker>\n"
    r += "      <ResourceCompiler Options=\"\" Required=\"no\"/>\n"
    r += "      <General OutputFile=\"../../run/linux_x64_debug/$(ProjectName)\" IntermediateDirectory=\"../../build/linux_x64_debug/\" Command=\"$(OutputFile)\" CommandArguments=\"\" UseSeparateDebugArgs=\"no\" DebugArguments=\"\" WorkingDirectory=\"../../run/linux_x64_debug/\" PauseExecWhenProcTerminates=\"yes\" IsGUIProgram=\"no\" IsEnabled=\"yes\"/>\n"
    r += "      <BuildSystem Name=\"Default\"/>\n"
    r += "      <Environment EnvVarSetName=\"&lt;Use Defaults&gt;\" DbgSetName=\"&lt;Use Defaults&gt;\">\n"
    r += "        <![CDATA[]]>\n"
    r += "      </Environment>\n"
    r += "      <Debugger IsRemote=\"no\" RemoteHostName=\"\" RemoteHostPort=\"\" DebuggerPath=\"\" IsExtended=\"no\">\n"
    r += "        <DebuggerSearchPaths/>\n"
    r += "        <PostConnectCommands/>\n"
    r += "        <StartupCommands/>\n"
    r += "      </Debugger>\n"
    r += "      <PreBuild/>\n"
    r += "      <PostBuild/>\n"
    r += "      <CustomBuild Enabled=\"no\">\n"
    r += "        <RebuildCommand/>\n"
    r += "        <CleanCommand/>\n"
    r += "        <BuildCommand/>\n"
    r += "        <PreprocessFileCommand/>\n"
    r += "        <SingleFileCommand/>\n"
    r += "        <MakefileGenerationCommand/>\n"
    r += "        <ThirdPartyToolName>None</ThirdPartyToolName>\n"
    r += "        <WorkingDirectory/>\n"
    r += "      </CustomBuild>\n"
    r += "      <AdditionalRules>\n"
    r += "        <CustomPostBuild/>\n"
    r += "        <CustomPreBuild/>\n"
    r += "      </AdditionalRules>\n"
    r += "      <Completion EnableCpp11=\"no\" EnableCpp14=\"no\">\n"
    r += "        <ClangCmpFlagsC/>\n"
    r += "        <ClangCmpFlags/>\n"
    r += "        <ClangPP/>\n"
    r += "        <SearchPaths/>\n"
    r += "      </Completion>\n"
    r += "    </Configuration>\n"

    r += "    <Configuration Name=\"Linux / x64 / Debug (no asan)\" CompilerType=\"GCC\" DebuggerType=\"GNU gdb debugger\" Type=\"Executable\" BuildCmpWithGlobalSettings=\"append\" BuildLnkWithGlobalSettings=\"append\" BuildResWithGlobalSettings=\"append\">\n"
    r += "      <Compiler Options=\"-g;-O0;-Wall\" C_Options=\"%s\" Assembler=\"\" Required=\"yes\" PreCompiledHeader=\"\" PCHInCommandLine=\"no\" PCHFlags=\"\" PCHFlagsPolicy=\"0\">\n" % prjboot_util.inline_opts(";", [x for x in (standard_c.get_c_compiler_flags_debug_gcc() + standard_c.get_c_compiler_flags_linux_gcc()) if x != "-fsanitize=address"])
    r += "      </Compiler>\n"
    r += "      <Linker Options=\"\" Required=\"yes\">\n"
    r += prjboot_util.deco_if_not_empty("", prjboot_util.format_xml_tag_value_list("        ", "Library", "Value", [x for x in standard_c.get_c_linker_flags_debug_gcc() if x != "-lasan"], prjboot_util.filter_remove_dash_l), "\n")
    r += "      </Linker>\n"
    r += "      <ResourceCompiler Options=\"\" Required=\"no\"/>\n"
    r += "      <General OutputFile=\"../../run/linux_x64_debug/$(ProjectName)\" IntermediateDirectory=\"../../build/linux_x64_debug/\" Command=\"$(OutputFile)\" CommandArguments=\"\" UseSeparateDebugArgs=\"no\" DebugArguments=\"\" WorkingDirectory=\"../../run/linux_x64_debug/\" PauseExecWhenProcTerminates=\"yes\" IsGUIProgram=\"no\" IsEnabled=\"yes\"/>\n"
    r += "      <BuildSystem Name=\"Default\"/>\n"
    r += "      <Environment EnvVarSetName=\"&lt;Use Defaults&gt;\" DbgSetName=\"&lt;Use Defaults&gt;\">\n"
    r += "        <![CDATA[]]>\n"
    r += "      </Environment>\n"
    r += "      <Debugger IsRemote=\"no\" RemoteHostName=\"\" RemoteHostPort=\"\" DebuggerPath=\"\" IsExtended=\"no\">\n"
    r += "        <DebuggerSearchPaths/>\n"
    r += "        <PostConnectCommands/>\n"
    r += "        <StartupCommands/>\n"
    r += "      </Debugger>\n"
    r += "      <PreBuild/>\n"
    r += "      <PostBuild/>\n"
    r += "      <CustomBuild Enabled=\"no\">\n"
    r += "        <RebuildCommand/>\n"
    r += "        <CleanCommand/>\n"
    r += "        <BuildCommand/>\n"
    r += "        <PreprocessFileCommand/>\n"
    r += "        <SingleFileCommand/>\n"
    r += "        <MakefileGenerationCommand/>\n"
    r += "        <ThirdPartyToolName>None</ThirdPartyToolName>\n"
    r += "        <WorkingDirectory/>\n"
    r += "      </CustomBuild>\n"
    r += "      <AdditionalRules>\n"
    r += "        <CustomPostBuild/>\n"
    r += "        <CustomPreBuild/>\n"
    r += "      </AdditionalRules>\n"
    r += "      <Completion EnableCpp11=\"no\" EnableCpp14=\"no\">\n"
    r += "        <ClangCmpFlagsC/>\n"
    r += "        <ClangCmpFlags/>\n"
    r += "        <ClangPP/>\n"
    r += "        <SearchPaths/>\n"
    r += "      </Completion>\n"
    r += "    </Configuration>\n"

    r += "    <Configuration Name=\"Linux / x64 / Debug (LLVM)\" CompilerType=\"CLANG-%s\" DebuggerType=\"GNU gdb debugger\" Type=\"Executable\" BuildCmpWithGlobalSettings=\"append\" BuildLnkWithGlobalSettings=\"append\" BuildResWithGlobalSettings=\"append\">\n" % standard_c.get_clang_version()
    r += "      <Compiler Options=\"-g;-O0;-Wall\" C_Options=\"%s\" Assembler=\"\" Required=\"yes\" PreCompiledHeader=\"\" PCHInCommandLine=\"no\" PCHFlags=\"\" PCHFlagsPolicy=\"0\">\n" % prjboot_util.inline_opts(";", standard_c.get_c_compiler_flags_debug_gcc() + standard_c.get_c_compiler_flags_linux_gcc())
    r += "      </Compiler>\n"
    r += "      <Linker Options=\"\" Required=\"yes\">\n"
    r += prjboot_util.deco_if_not_empty("", prjboot_util.format_xml_tag_value_list("        ", "Library", "Value", standard_c.get_c_linker_flags_debug_gcc(), prjboot_util.filter_remove_dash_l), "\n")
    r += "      </Linker>\n"
    r += "      <ResourceCompiler Options=\"\" Required=\"no\"/>\n"
    r += "      <General OutputFile=\"../../run/linux_x64_debug/$(ProjectName)\" IntermediateDirectory=\"../../build/linux_x64_debug/\" Command=\"$(OutputFile)\" CommandArguments=\"\" UseSeparateDebugArgs=\"no\" DebugArguments=\"\" WorkingDirectory=\"../../run/linux_x64_debug/\" PauseExecWhenProcTerminates=\"yes\" IsGUIProgram=\"no\" IsEnabled=\"yes\"/>\n"
    r += "      <BuildSystem Name=\"Default\"/>\n"
    r += "      <Environment EnvVarSetName=\"&lt;Use Defaults&gt;\" DbgSetName=\"&lt;Use Defaults&gt;\">\n"
    r += "        <![CDATA[]]>\n"
    r += "      </Environment>\n"
    r += "      <Debugger IsRemote=\"no\" RemoteHostName=\"\" RemoteHostPort=\"\" DebuggerPath=\"\" IsExtended=\"no\">\n"
    r += "        <DebuggerSearchPaths/>\n"
    r += "        <PostConnectCommands/>\n"
    r += "        <StartupCommands/>\n"
    r += "      </Debugger>\n"
    r += "      <PreBuild/>\n"
    r += "      <PostBuild/>\n"
    r += "      <CustomBuild Enabled=\"no\">\n"
    r += "        <RebuildCommand/>\n"
    r += "        <CleanCommand/>\n"
    r += "        <BuildCommand/>\n"
    r += "        <PreprocessFileCommand/>\n"
    r += "        <SingleFileCommand/>\n"
    r += "        <MakefileGenerationCommand/>\n"
    r += "        <ThirdPartyToolName>None</ThirdPartyToolName>\n"
    r += "        <WorkingDirectory/>\n"
    r += "      </CustomBuild>\n"
    r += "      <AdditionalRules>\n"
    r += "        <CustomPostBuild/>\n"
    r += "        <CustomPreBuild/>\n"
    r += "      </AdditionalRules>\n"
    r += "      <Completion EnableCpp11=\"no\" EnableCpp14=\"no\">\n"
    r += "        <ClangCmpFlagsC/>\n"
    r += "        <ClangCmpFlags/>\n"
    r += "        <ClangPP/>\n"
    r += "        <SearchPaths/>\n"
    r += "      </Completion>\n"
    r += "    </Configuration>\n"

    r += "    <Configuration Name=\"Linux / x64 / Release\" CompilerType=\"GCC\" DebuggerType=\"GNU gdb debugger\" Type=\"Executable\" BuildCmpWithGlobalSettings=\"append\" BuildLnkWithGlobalSettings=\"append\" BuildResWithGlobalSettings=\"append\">\n"
    r += "      <Compiler Options=\"-O2;-Wall\" C_Options=\"%s\" Assembler=\"\" Required=\"yes\" PreCompiledHeader=\"\" PCHInCommandLine=\"no\" PCHFlags=\"\" PCHFlagsPolicy=\"0\">\n" % prjboot_util.inline_opts(";", standard_c.get_c_compiler_flags_release_gcc() + standard_c.get_c_compiler_flags_linux_gcc())
    r += "        <Preprocessor Value=\"NDEBUG\"/>\n"
    r += "      </Compiler>\n"
    r += "      <Linker Options=\"\" Required=\"yes\">\n"
    r += prjboot_util.deco_if_not_empty("", prjboot_util.format_xml_tag_value_list("        ", "Library", "Value", standard_c.get_c_linker_flags_release_gcc(), prjboot_util.filter_remove_dash_l), "\n")
    r += "      </Linker>\n"
    r += "      <ResourceCompiler Options=\"\" Required=\"no\"/>\n"
    r += "      <General OutputFile=\"../../run/linux_x64_release/$(ProjectName)\" IntermediateDirectory=\"../../build/linux_x64_release/\" Command=\"$(OutputFile)\" CommandArguments=\"\" UseSeparateDebugArgs=\"no\" DebugArguments=\"\" WorkingDirectory=\"../../run/linux_x64_release/\" PauseExecWhenProcTerminates=\"yes\" IsGUIProgram=\"no\" IsEnabled=\"yes\"/>\n"
    r += "      <BuildSystem Name=\"Default\"/>\n"
    r += "      <Environment EnvVarSetName=\"&lt;Use Defaults&gt;\" DbgSetName=\"&lt;Use Defaults&gt;\">\n"
    r += "        <![CDATA[]]>\n"
    r += "      </Environment>\n"
    r += "      <Debugger IsRemote=\"no\" RemoteHostName=\"\" RemoteHostPort=\"\" DebuggerPath=\"\" IsExtended=\"no\">\n"
    r += "        <DebuggerSearchPaths/>\n"
    r += "        <PostConnectCommands/>\n"
    r += "        <StartupCommands/>\n"
    r += "      </Debugger>\n"
    r += "      <PreBuild/>\n"
    r += "      <PostBuild/>\n"
    r += "      <CustomBuild Enabled=\"no\">\n"
    r += "        <RebuildCommand/>\n"
    r += "        <CleanCommand/>\n"
    r += "        <BuildCommand/>\n"
    r += "        <PreprocessFileCommand/>\n"
    r += "        <SingleFileCommand/>\n"
    r += "        <MakefileGenerationCommand/>\n"
    r += "        <ThirdPartyToolName>None</ThirdPartyToolName>\n"
    r += "        <WorkingDirectory/>\n"
    r += "      </CustomBuild>\n"
    r += "      <AdditionalRules>\n"
    r += "        <CustomPostBuild/>\n"
    r += "        <CustomPreBuild/>\n"
    r += "      </AdditionalRules>\n"
    r += "      <Completion EnableCpp11=\"no\" EnableCpp14=\"no\">\n"
    r += "        <ClangCmpFlagsC/>\n"
    r += "        <ClangCmpFlags/>\n"
    r += "        <ClangPP/>\n"
    r += "        <SearchPaths/>\n"
    r += "      </Completion>\n"
    r += "    </Configuration>\n"

    r += "    <Configuration Name=\"Linux / x64 / Release (LLVM)\" CompilerType=\"CLANG-%s\" DebuggerType=\"GNU gdb debugger\" Type=\"Executable\" BuildCmpWithGlobalSettings=\"append\" BuildLnkWithGlobalSettings=\"append\" BuildResWithGlobalSettings=\"append\">\n" % standard_c.get_clang_version()
    r += "      <Compiler Options=\"-O2;-Wall\" C_Options=\"%s\" Assembler=\"\" Required=\"yes\" PreCompiledHeader=\"\" PCHInCommandLine=\"no\" PCHFlags=\"\" PCHFlagsPolicy=\"0\">\n" % prjboot_util.inline_opts(";", standard_c.get_c_compiler_flags_release_gcc() + standard_c.get_c_compiler_flags_linux_gcc())
    r += "        <Preprocessor Value=\"NDEBUG\"/>\n"
    r += "      </Compiler>\n"
    r += "      <Linker Options=\"\" Required=\"yes\">\n"
    r += prjboot_util.deco_if_not_empty("", prjboot_util.format_xml_tag_value_list("        ", "Library", "Value", standard_c.get_c_linker_flags_release_gcc(), prjboot_util.filter_remove_dash_l), "\n")
    r += "      </Linker>\n"
    r += "      <ResourceCompiler Options=\"\" Required=\"no\"/>\n"
    r += "      <General OutputFile=\"../../run/linux_x64_release/$(ProjectName)\" IntermediateDirectory=\"../../build/linux_x64_release/\" Command=\"$(OutputFile)\" CommandArguments=\"\" UseSeparateDebugArgs=\"no\" DebugArguments=\"\" WorkingDirectory=\"../../run/linux_x64_release/\" PauseExecWhenProcTerminates=\"yes\" IsGUIProgram=\"no\" IsEnabled=\"yes\"/>\n"
    r += "      <BuildSystem Name=\"Default\"/>\n"
    r += "      <Environment EnvVarSetName=\"&lt;Use Defaults&gt;\" DbgSetName=\"&lt;Use Defaults&gt;\">\n"
    r += "        <![CDATA[]]>\n"
    r += "      </Environment>\n"
    r += "      <Debugger IsRemote=\"no\" RemoteHostName=\"\" RemoteHostPort=\"\" DebuggerPath=\"\" IsExtended=\"no\">\n"
    r += "        <DebuggerSearchPaths/>\n"
    r += "        <PostConnectCommands/>\n"
    r += "        <StartupCommands/>\n"
    r += "      </Debugger>\n"
    r += "      <PreBuild/>\n"
    r += "      <PostBuild/>\n"
    r += "      <CustomBuild Enabled=\"no\">\n"
    r += "        <RebuildCommand/>\n"
    r += "        <CleanCommand/>\n"
    r += "        <BuildCommand/>\n"
    r += "        <PreprocessFileCommand/>\n"
    r += "        <SingleFileCommand/>\n"
    r += "        <MakefileGenerationCommand/>\n"
    r += "        <ThirdPartyToolName>None</ThirdPartyToolName>\n"
    r += "        <WorkingDirectory/>\n"
    r += "      </CustomBuild>\n"
    r += "      <AdditionalRules>\n"
    r += "        <CustomPostBuild/>\n"
    r += "        <CustomPreBuild/>\n"
    r += "      </AdditionalRules>\n"
    r += "      <Completion EnableCpp11=\"no\" EnableCpp14=\"no\">\n"
    r += "        <ClangCmpFlagsC/>\n"
    r += "        <ClangCmpFlags/>\n"
    r += "        <ClangPP/>\n"
    r += "        <SearchPaths/>\n"
    r += "      </Completion>\n"
    r += "    </Configuration>\n"

    r += "  </Settings>\n"
    r += "</CodeLite_Project>\n"

    ba_r = bytearray()
    ba_r.extend(map(ord, r))
    return ba_r

def generate_codelite15_c(target_dir, project_name):

    # base folders / base structure
    prj_fullname_base = path_utils.concat_path(target_dir, project_name)
    base_prj = path_utils.concat_path(prj_fullname_base, "proj")
    base_src = path_utils.concat_path(prj_fullname_base, "src")

    # generate the actual C Codelite project file
    base_prj_codelite15_c = path_utils.concat_path(base_prj, "codelite15_c")
    prjboot_util.makedir_if_needed(base_prj_codelite15_c)
    base_prj_codelite_fn = path_utils.concat_path(base_prj_codelite15_c, "%s.project" % project_name)
    if not prjboot_util.writecontents(base_prj_codelite_fn, codelite15_c_projfile_contents(project_name)):
        return False, "Failed creating [%s]" % base_prj_codelite_fn

    # gitignore
    gitignore_filename = path_utils.concat_path(prj_fullname_base, ".gitignore")
    prjboot_util.add_to_gitignore_if_needed(gitignore_filename, "proj/codelite15_c/%s.mk" % project_name)
    prjboot_util.add_to_gitignore_if_needed(gitignore_filename, "proj/codelite15_c/%s.txt" % project_name)
    prjboot_util.add_to_gitignore_if_needed(gitignore_filename, "proj/codelite15_c/compile_flags.txt")

    # main C file
    base_src_main_c_fn = path_utils.concat_path(base_src, "main.c")
    if not prjboot_util.writecontents(base_src_main_c_fn, standard_c.get_main_c_app()):
        return False, "Failed creating [%s]" % base_src_main_c_fn

    # secondary C file
    base_src_subfolder = path_utils.concat_path(base_src, "subfolder")
    prjboot_util.makedir_if_needed(base_src_subfolder)
    base_src_subfolder_secondary_c_fn = path_utils.concat_path(base_src_subfolder, "second.c")
    if not prjboot_util.writecontents(base_src_subfolder_secondary_c_fn, prjboot_util.secondary_c_app()):
        return False, "Failed creating [%s]" % base_src_subfolder_secondary_c_fn

    return True, None
